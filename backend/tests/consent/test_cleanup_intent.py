"""Exercise the canonical withdrawal body at its ORM boundaries without a database."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from django.db.models import F

from modules.identity import consent
from modules.identity.consent_policy import qualifying_consents
from modules.identity.models import Learner
from modules.operations.models import ConsentCleanupIntent


@pytest.fixture
def withdrawal(monkeypatch):
    now = datetime(2026, 11, 21, 12, tzinfo=timezone.utc)
    guardian = SimpleNamespace(pk=1, is_authenticated=True, is_active=True)
    tenant = SimpleNamespace(pk=uuid4())
    learner = SimpleNamespace(pk=uuid4(), tenant=tenant, tenant_id=tenant.pk, authorization_generation=7)
    relationship = SimpleNamespace(learner_id=learner.pk, guardian_id=guardian.pk)
    record = SimpleNamespace(pk=uuid4(), purpose="tutoring", relationship=relationship, withdrawn_at=None,
                             save=Mock())

    consent_rows = Mock()
    consent_rows.select_related.return_value.get.return_value = record
    consent_rows.select_for_update.return_value.select_related.return_value.get.return_value = record
    learner_rows = Mock()
    learner_rows.select_for_update.return_value.get.return_value = learner
    memberships = Mock()
    memberships.filter.return_value.exists.return_value = True
    candidates = Mock()
    qualifying = Mock(return_value=candidates)
    create_intent = Mock()
    clock = Mock(return_value=now)
    monkeypatch.setattr(consent.ConsentRecord, "objects", consent_rows)
    monkeypatch.setattr(consent.Learner, "objects", learner_rows)
    monkeypatch.setattr(consent.Membership, "objects", memberships)
    monkeypatch.setattr(consent, "qualifying_consents", qualifying)
    monkeypatch.setattr(consent.timezone, "now", clock)
    monkeypatch.setattr(ConsentCleanupIntent.objects, "create", create_intent)

    return SimpleNamespace(now=now, clock=clock, guardian=guardian, learner=learner, record=record,
                           qualifying=qualifying, candidates=candidates, memberships=memberships,
                           learner_rows=learner_rows, consent_rows=consent_rows, create_intent=create_intent,
                           run=lambda: consent.withdraw_consent.__wrapped__(guardian, record.pk))


@pytest.mark.parametrize("denial", ["anonymous", "inactive", "wrong-guardian", "no-live-tenant-membership"])
def test_denied_withdrawal_never_records_cleanup_or_fences_learner(withdrawal, denial):
    case = withdrawal
    if denial == "anonymous":
        case.guardian.is_authenticated = False
    elif denial == "inactive":
        case.guardian.is_active = False
    elif denial == "wrong-guardian":
        case.record.relationship.guardian_id += 1
    else:
        case.memberships.filter.return_value.exists.return_value = False

    with pytest.raises(PermissionError):
        case.run()

    if denial == "no-live-tenant-membership":
        case.memberships.filter.assert_called_once_with(
            actor=case.guardian, actor__is_active=True, tenant_id=case.learner.tenant_id, role="guardian", active=True,
        )
    assert case.record.withdrawn_at is None
    case.record.save.assert_not_called()
    case.learner_rows.filter.assert_not_called()
    case.qualifying.assert_not_called()
    case.create_intent.assert_not_called()


@pytest.mark.parametrize("purpose", ["guardian_reporting", "teacher_reporting"])
def test_reporting_withdrawal_retains_generation_fence_without_tutoring_cleanup(withdrawal, purpose):
    case = withdrawal
    case.record.purpose = purpose

    assert case.run() is case.record

    assert case.record.withdrawn_at == case.now
    case.record.save.assert_called_once_with(update_fields=["withdrawn_at"])
    case.learner_rows.filter.assert_called_once_with(pk=case.learner.pk)
    case.learner_rows.filter.return_value.update.assert_called_once_with(
        authorization_generation=F("authorization_generation") + 1,
    )
    case.qualifying.assert_not_called()
    case.create_intent.assert_not_called()


@pytest.mark.parametrize(
    ("was_qualifying", "own_remains", "any_remains", "uploader_scope"),
    [
        (False, False, False, "none"),
        (True, True, True, "none"),
        (True, False, True, "guardian"),
        (True, False, False, "learner-wide"),
    ],
    ids=["ineffective", "same-guardian-overlap", "other-guardian-overlap", "last-qualifying-grant"],
)
def test_first_withdrawal_records_only_the_effective_loss(withdrawal, was_qualifying, own_remains,
                                                    any_remains, uploader_scope):
    case = withdrawal

    def filter_candidates(**filters):
        if "pk" in filters:
            assert filters == {"pk": case.record.pk}
            assert case.record.withdrawn_at is None
            return Mock(**{"exists.return_value": was_qualifying})
        assert filters == {"relationship__guardian_id": case.guardian.pk}
        case.record.save.assert_called_once_with(update_fields=["withdrawn_at"])
        return Mock(**{"exists.return_value": own_remains})

    case.candidates.filter.side_effect = filter_candidates
    case.candidates.exists.return_value = any_remains

    assert case.run() is case.record

    assert case.record.withdrawn_at == case.now
    case.learner_rows.select_for_update.return_value.get.assert_called_once_with(pk=case.learner.pk)
    case.clock.assert_called_once_with()
    case.qualifying.assert_called_once_with(case.learner, "tutoring", case.now)
    case.record.save.assert_called_once_with(update_fields=["withdrawn_at"])
    case.learner_rows.filter.assert_called_once_with(pk=case.learner.pk)
    case.learner_rows.filter.return_value.update.assert_called_once_with(
        authorization_generation=F("authorization_generation") + 1,
    )
    if uploader_scope == "none":
        case.create_intent.assert_not_called()
    else:
        case.create_intent.assert_called_once_with(
            consent=case.record, learner=case.learner, tenant_id=case.learner.tenant_id, purpose="tutoring",
            uploader_id=case.guardian.pk if uploader_scope == "guardian" else None,
            cutoff_generation=7, policy_version="effective-loss-v1", disposition="full_purge",
        )


def test_already_withdrawn_consent_never_backfills_an_intent(withdrawal):
    case = withdrawal
    case.record.withdrawn_at = case.now

    assert case.run() is case.record

    case.clock.assert_not_called()
    case.record.save.assert_not_called()
    case.learner_rows.filter.assert_not_called()
    case.qualifying.assert_not_called()
    case.create_intent.assert_not_called()


def test_shared_consent_query_pins_scope_eligibility_and_time_without_evaluating():
    learner = Learner(id=uuid4(), tenant_id=uuid4())
    now = datetime(2026, 11, 21, 12, tzinfo=timezone.utc)
    where = qualifying_consents(learner, "tutoring", now).query.where

    assert where.connector == "AND" and not where.negated
    filters = {node.lhs.target.name: (node.lookup_name, node.rhs) for node in where.children
               if hasattr(node, "lookup_name")}
    membership_query = filters.pop("guardian")[1]
    assert filters == {
        "learner": ("exact", learner.pk),
        "purpose": ("exact", "tutoring"),
        "is_active": ("exact", True),
        "verified_at": ("lte", now),
        "revoked_at": ("isnull", True),
        "granted_at": ("lte", now),
        "expires_at": ("gt", now),
        "withdrawn_at": ("isnull", True),
    }
    assert membership_query.where.connector == "AND" and not membership_query.where.negated
    assert {
        node.lhs.target.name: (node.lookup_name, node.rhs) for node in membership_query.where.children
    } == {"tenant": ("exact", learner.tenant_id), "role": ("exact", "guardian"), "active": ("exact", True)}
    assert [column.target.attname for column in membership_query.select] == ["actor_id"]
    assert {
        lookup.lhs.target.name for node in where.children if getattr(node, "negated", False)
        for lookup in node.children if lookup.lookup_name == "exact" and lookup.rhs == ""
    } == {"verification_ref", "notice_version", "notice_locale", "evidence_ref"}
