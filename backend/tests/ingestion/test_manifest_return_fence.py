"""Exercise authorization changes after a real local manifest read, without a database."""

import hashlib
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from django.utils import timezone

from modules.ingestion import service
from tests.ingestion.test_dispatch_fence import broker


@pytest.fixture
def manifest(broker, monkeypatch):
    assert broker.run().status == "needs_review"
    broker.row.quota = SimpleNamespace(
        learner_id=broker.resource.learner_id,
        course_id=broker.resource.course_id,
        learner=SimpleNamespace(tenant_id=uuid4()),
    )
    upload_query = Mock()
    upload_query.get.side_effect = lambda **_: SimpleNamespace(**vars(broker.row))
    monkeypatch.setattr(service.Upload.objects, "select_related", lambda *_: upload_query)
    grant_query = Mock()
    grant_query.first.return_value = SimpleNamespace(pk=uuid4())
    member_query = Mock()
    member_query.exists.return_value = True
    monkeypatch.setattr(service.ReviewGrant.objects, "filter", lambda **_: grant_query)
    monkeypatch.setattr(service.Membership.objects, "filter", lambda **_: member_query)

    read = broker.store.read

    def change_during_read(change):
        def read_then_change(object_id, suffix, maximum):
            assert (object_id, suffix, maximum) == (str(broker.row.id), "manifest", service.MAX_OUTPUT)
            data = read(object_id, suffix, maximum)
            change()
            return data

        controlled_read = Mock(side_effect=read_then_change)
        monkeypatch.setattr(broker.store, "read", controlled_read)
        return controlled_read

    def publish(expires=None):
        broker.row.status = "private_ready"
        broker.row.rights_evidence = "fixture.rights"
        broker.row.rights_expires = expires or timezone.now() + timedelta(minutes=1)

    return SimpleNamespace(
        broker=broker, publish=publish, change_during_read=change_during_read,
        requester=SimpleNamespace(pk=uuid4(), is_authenticated=True, is_active=True),
        grant_query=grant_query,
    )


def test_resolve_discards_manifest_if_consent_withdrawn_and_regranted_during_read(manifest):
    manifest.publish()
    broker = manifest.broker

    def change_authorization_generation():
        # A new consent makes authorization live again while fencing the original upload.
        broker.resource.learner.authorization_generation += 1

    read = manifest.change_during_read(change_authorization_generation)
    with pytest.raises(service.Denied):
        service.resolve(manifest.requester, broker.row.id, broker.store)
    read.assert_called_once()


def test_resolve_discards_manifest_if_rights_expire_during_read(manifest, monkeypatch):
    now = timezone.now()
    manifest.publish(now + timedelta(seconds=1))
    broker = manifest.broker
    clock = Mock(return_value=now)
    monkeypatch.setattr(service.timezone, "now", clock)

    def expire_rights():
        clock.return_value = broker.row.rights_expires

    read = manifest.change_during_read(expire_rights)
    with pytest.raises(service.Denied):
        service.resolve(manifest.requester, broker.row.id, broker.store)
    read.assert_called_once()


def test_review_discards_manifest_if_reviewer_grant_removed_during_read(manifest):
    broker = manifest.broker

    def remove_grant():
        manifest.grant_query.first.return_value = None

    read = manifest.change_during_read(remove_grant)
    with pytest.raises(service.Denied):
        service.review_manifest(manifest.requester, broker.row.id, broker.store)
    read.assert_called_once()


@pytest.mark.parametrize("operation", ["resolve", "review_manifest"])
@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("source_sha256", "0" * 64),
        ("generation", 2),
        ("manifest_sha256", "0" * 64),
        ("dispatch_id", uuid4()),
    ],
)
def test_manifest_drops_old_bytes_if_current_binding_changes(manifest, operation, field, replacement):
    broker = manifest.broker
    if operation == "resolve":
        manifest.publish()

    read = manifest.change_during_read(lambda: setattr(broker.row, field, replacement))
    with pytest.raises(service.Conflict):
        getattr(service, operation)(manifest.requester, broker.row.id, broker.store)
    read.assert_called_once()


def test_resolve_discards_manifest_if_saved_scope_mutates_in_place(manifest):
    manifest.publish()
    broker = manifest.broker

    def change_version():
        broker.resource.edition_version += 1
        broker.row.scope["version"] = broker.resource.edition_version

    read = manifest.change_during_read(change_version)
    with pytest.raises(service.Conflict):
        service.resolve(manifest.requester, broker.row.id, broker.store)
    read.assert_called_once()


@pytest.mark.parametrize("operation", ["resolve", "review_manifest"])
def test_manifest_returns_for_unchanged_current_binding(manifest, operation):
    broker = manifest.broker
    if operation == "resolve":
        manifest.publish()
    assert manifest.requester.pk != broker.row.actor_id

    result = getattr(service, operation)(manifest.requester, broker.row.id, broker.store)

    assert result["source_sha256"] == broker.row.source_sha256
    assert result["generation"] == broker.row.generation
    assert result["dispatch_id"] == str(broker.row.dispatch_id)
    assert hashlib.sha256(service.canonical(result)).hexdigest() == broker.row.manifest_sha256
