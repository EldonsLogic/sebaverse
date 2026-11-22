"""Exercise broker dispatch with authored adapters and no database connection."""

import hashlib
import json
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from modules.ingestion import service
from modules.ingestion.storage import PrivateObjects


@pytest.fixture
def broker(tmp_path, monkeypatch):
    data = b"%PDF-authored dispatch fixture"
    actor = SimpleNamespace(pk=uuid4(), is_authenticated=True, is_active=True)
    resource = SimpleNamespace(
        learner_id=uuid4(), course_id=uuid4(), edition_id="fixture.edition",
        edition_version=1, purpose="tutoring", kind="file",
        learner=SimpleNamespace(authorization_generation=1),
    )
    row = SimpleNamespace(
        id=uuid4(), actor=actor, actor_id=actor.pk, resource_id=uuid4(),
        scope=service.scope(resource), authorization_generation=1,
        source_sha256=hashlib.sha256(data).hexdigest(), media_type="application/pdf",
        status="quarantined", generation=1, dispatch_id=None, attempts=0,
        writer_active=False, stored_bytes=len(data), manifest_bytes=0, held_bytes=0,
    )
    quota = SimpleNamespace(limit_bytes=10000, used_bytes=len(data), reserved_bytes=0, save=Mock())

    def read_upload():
        upload = SimpleNamespace(**vars(row))
        upload.save = lambda: vars(row).update({k: v for k, v in vars(upload).items() if k != "save"})
        return upload

    authorization = Mock(return_value=resource)
    monkeypatch.setattr(service.transaction, "atomic", nullcontext)
    monkeypatch.setattr(service.transaction, "get_autocommit", lambda: True)
    monkeypatch.setattr(service, "locked", lambda upload_id: (quota, read_upload()))
    monkeypatch.setattr(service, "authorized_resource", authorization)

    store = PrivateObjects(tmp_path / "private")
    store.put(str(row.id), [data], len(data))
    scanner = Mock(asset_id="fixture-scanner.v1")
    scanner.scan.return_value = {"asset_id": scanner.asset_id, "sha256": row.source_sha256, "status": "clean"}
    parser = Mock(asset_id="fixture-parser.v1")

    def result_for(source, expected):
        return {**expected, "page_count": 1, "quality": "needs_review",
                "blocks": [{"page": 1, "anchor": "p1.b1", "text": source.decode()}]}

    parser.parse.side_effect = result_for
    assets = service.RuntimeAssets(tuple(
        {"kind": kind, "id": adapter.asset_id, "reviewed": True,
         "scope": "authored_fixture_only", "source_hashes": [row.source_sha256]}
        for kind, adapter in [("scanner", scanner), ("parser", parser)]
    ))
    return SimpleNamespace(
        actor=actor, row=row, resource=resource, quota=quota, authorization=authorization,
        scanner=scanner, parser=parser, store=store, result_for=result_for,
        run=lambda: service.process(row.id, store, scanner, parser, assets),
        manifest=store.path(str(row.id), "manifest"),
    )


def test_clean_scan_after_withdrawal_never_dispatches_parser(broker):
    def withdraw_during_scan(_source):
        service.withdraw(broker.actor, broker.row.id, broker.store)
        return broker.scanner.scan.return_value

    broker.scanner.scan.side_effect = withdraw_during_scan
    assert broker.run().status == "deleted"
    broker.parser.parse.assert_not_called()
    assert broker.quota.used_bytes == 0
    assert not broker.manifest.exists()


@pytest.mark.parametrize("access_change", ["revoked", "withdrawn_then_regranted"])
def test_clean_scan_cannot_dispatch_after_authorization_changes(broker, access_change):
    def change_access_during_scan(_source):
        if access_change == "revoked":
            broker.authorization.return_value = None
        else:
            # Live grants can be valid again while the original dispatch is stale.
            broker.resource.learner.authorization_generation += 1
        return broker.scanner.scan.return_value

    broker.scanner.scan.side_effect = change_access_during_scan
    assert broker.run().status == "withdrawn"
    assert broker.row.generation == 2
    broker.parser.parse.assert_not_called()
    assert not broker.manifest.exists()


@pytest.mark.parametrize("superseded_during", ["scan", "parse"])
def test_old_dispatch_leaves_newer_processing_owner_untouched(broker, superseded_during):
    replacement_dispatch = uuid4()

    def supersede():
        broker.row.dispatch_id = replacement_dispatch
        broker.row.generation += 1

    def supersede_during_scan(_source):
        supersede()
        return broker.scanner.scan.return_value

    def supersede_during_parse(source, expected):
        supersede()
        return broker.result_for(source, expected)

    if superseded_during == "scan":
        broker.scanner.scan.side_effect = supersede_during_scan
    else:
        broker.parser.parse.side_effect = supersede_during_parse
    current = broker.run()
    assert current.status == "processing"
    assert current.dispatch_id == replacement_dispatch
    assert current.generation == 2
    if superseded_during == "scan":
        broker.parser.parse.assert_not_called()
    assert not broker.manifest.exists()


def test_parser_cannot_redefine_its_expected_provenance(broker):
    def forge_dispatch(source, expected):
        expected["dispatch_id"] = str(uuid4())
        return broker.result_for(source, expected)

    broker.parser.parse.side_effect = forge_dispatch
    current = broker.run()
    assert current.status == "quarantined"
    assert current.failure_code == "scan_or_parse_failed"
    assert broker.quota.used_bytes == broker.row.stored_bytes
    assert not broker.manifest.exists()


def test_unchanged_authorized_dispatch_stores_scoped_result_for_review(broker):
    current = broker.run()
    broker.scanner.scan.assert_called_once()
    broker.parser.parse.assert_called_once()
    assert current.status == "needs_review"
    output = json.loads(broker.manifest.read_bytes())
    assert output["dispatch_id"] == str(current.dispatch_id)
    assert output["generation"] == current.generation
    assert output["quality"] == "needs_review"
    assert broker.quota.used_bytes == broker.row.stored_bytes + current.manifest_bytes


def test_recorded_asset_ids_match_reviewed_dispatch_after_callback_mutation(broker):
    scanner_id, parser_id = broker.scanner.asset_id, broker.parser.asset_id

    def scan(source):
        broker.scanner.asset_id = "unreviewed-scanner"
        return broker.scanner.scan.return_value

    def parse(source, expected):
        broker.parser.asset_id = "unreviewed-parser"
        return broker.result_for(source, expected)

    broker.scanner.scan.side_effect = scan
    broker.parser.parse.side_effect = parse
    current = broker.run()
    assert current.status == "needs_review"
    assert (current.scan_id, current.parser_id) == (scanner_id, parser_id)
    assert json.loads(broker.manifest.read_bytes())["parser_id"] == parser_id


@pytest.mark.parametrize("parser_failed", [False, True])
def test_parser_already_running_when_access_is_revoked_cannot_advance(broker, parser_failed):
    def revoke_during_parse(source, expected):
        broker.authorization.return_value = None
        if parser_failed:
            raise ValueError("fixture parser failure")
        return broker.result_for(source, expected)

    broker.parser.parse.side_effect = revoke_during_parse
    current = broker.run()
    broker.parser.parse.assert_called_once()
    assert current.status == "withdrawn"
    assert current.generation == 2
    assert not broker.manifest.exists()
