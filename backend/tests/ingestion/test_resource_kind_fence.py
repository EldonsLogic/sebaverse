"""The live upload resource must still be a file when its saved scope matches."""

from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import Mock

import pytest
from django.utils import timezone

from modules.ingestion import service
from tests.ingestion.test_dispatch_fence import broker


def reclassify(broker):
    broker.resource.kind = "material"
    assert broker.row.scope == {
        "learner": str(broker.resource.learner_id),
        "course": str(broker.resource.course_id),
        "edition": broker.resource.edition_id,
        "version": broker.resource.edition_version,
        "purpose": broker.resource.purpose,
    }
    assert service.scope(broker.resource) == broker.row.scope
    assert broker.resource.learner.authorization_generation == broker.row.authorization_generation


def test_reclassified_resource_refuses_upload_bytes(broker, monkeypatch):
    source = broker.store.read(str(broker.row.id))
    broker.store.purge(str(broker.row.id))
    broker.row.status = "awaiting_bytes"
    broker.row.declared_bytes = len(source)
    broker.row.stored_bytes = 0
    broker.row.held_bytes = len(source)
    broker.quota.used_bytes = 0
    broker.quota.reserved_bytes = len(source)
    put = Mock(wraps=broker.store.put)
    monkeypatch.setattr(broker.store, "put", put)
    query = Mock()
    query.get.side_effect = lambda **_: {
        "status": broker.row.status, "generation": broker.row.generation,
    }
    monkeypatch.setattr(service.Upload.objects, "values", lambda *_: query)
    reclassify(broker)

    with pytest.raises(service.Denied):
        service.accept_bytes(broker.actor, broker.row.id, [source], broker.store)

    put.assert_not_called()
    assert broker.row.status == "awaiting_bytes"
    assert broker.quota.reserved_bytes == len(source)


def test_reclassified_resource_refuses_processing_before_scan(broker):
    reclassify(broker)

    with pytest.raises(service.Conflict):
        broker.run()

    broker.scanner.scan.assert_not_called()
    broker.parser.parse.assert_not_called()
    assert broker.row.status == "quarantined"
    assert broker.row.attempts == 0


@pytest.mark.parametrize("stage", ["scan", "parse"])
def test_reclassification_during_processing_discards_result(broker, stage):
    def scan(_source):
        reclassify(broker)
        return broker.scanner.scan.return_value

    def parse(source, expected):
        reclassify(broker)
        return broker.result_for(source, expected)

    if stage == "scan":
        broker.scanner.scan.side_effect = scan
    else:
        broker.parser.parse.side_effect = parse

    current = broker.run()

    assert current.status == "withdrawn"
    assert current.generation == 2
    assert broker.parser.parse.call_count == (1 if stage == "parse" else 0)
    assert broker.quota.used_bytes == broker.row.stored_bytes
    assert not broker.manifest.exists()


def test_previously_ready_upload_cannot_resolve_after_reclassification(broker, monkeypatch):
    assert broker.run().status == "needs_review"
    broker.row.status = "private_ready"
    broker.row.rights_evidence = "fixture.rights"
    broker.row.rights_expires = timezone.now() + timedelta(minutes=1)
    query = Mock()
    query.get.return_value = broker.row
    monkeypatch.setattr(service.Upload.objects, "select_related", lambda *_: query)
    read = Mock(wraps=broker.store.read)
    monkeypatch.setattr(broker.store, "read", read)
    assert service.resolve(broker.actor, broker.row.id, broker.store)["page_count"] == 1
    read.reset_mock()

    reclassify(broker)
    with pytest.raises(service.Denied):
        service.resolve(broker.actor, broker.row.id, broker.store)

    read.assert_not_called()


def test_file_resolution_preserves_independent_requester_authority(broker, monkeypatch):
    assert broker.run().status == "needs_review"
    broker.row.status = "private_ready"
    broker.row.rights_evidence = "fixture.rights"
    broker.row.rights_expires = timezone.now() + timedelta(minutes=1)
    query = Mock()
    query.get.return_value = broker.row
    monkeypatch.setattr(service.Upload.objects, "select_related", lambda *_: query)
    requester = SimpleNamespace(pk=uuid4(), is_authenticated=True, is_active=True)
    assert requester.pk != broker.row.actor_id
    broker.authorization.reset_mock()
    assert service.resolve(requester, broker.row.id, broker.store)["page_count"] == 1
    broker.authorization.assert_called_once_with(requester, broker.row.resource_id)
    broker.authorization.return_value = None
    with pytest.raises(service.Denied):
        service.resolve(requester, broker.row.id, broker.store)
