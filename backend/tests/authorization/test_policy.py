"""DEV-008 negatives first: no real identities or child records."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import pytest
from modules.access.policy import Scope, allowed

NOW = datetime(2026, 11, 17, tzinfo=timezone.utc)
KINDS = ['material', 'file', 'job', 'stream', 'export', 'vector', 'course', 'edition']


def valid(kind='material', role='learner'):
    return Scope(actor_active=True, member_active=True, role=role, tenant_matches=True,
                 learner_active=True, relationship_valid=True, consent_valid=True,
                 enrollment_valid=True, entitlement_valid=True, course_active=True,
                 edition_active=True, resource_active=True, version_matches=True,
                 purpose='tutoring' if role != 'teacher' else 'teacher_reporting', kind=kind)


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('failure', ['actor_active', 'member_active', 'tenant_matches', 'learner_active',
                                    'relationship_valid', 'consent_valid', 'enrollment_valid',
                                    'entitlement_valid', 'course_active', 'edition_active',
                                    'resource_active', 'version_matches'])
def test_each_resource_denies_each_missing_live_boundary(kind, failure):
    assert not allowed(replace(valid(kind), **{failure: False}))


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('role', ['staff', 'owner', 'model', '', 'admin'])
def test_staff_or_claimed_role_has_no_implicit_learner_access(kind, role):
    assert not allowed(replace(valid(kind), role=role))


@pytest.mark.parametrize('kind', KINDS)
def test_unknown_purpose_or_capability_is_denied(kind):
    assert not allowed(replace(valid(kind), purpose='training'))
    assert not allowed(replace(valid(kind), kind='answer_key'))


@pytest.mark.parametrize('role,purpose', [('learner', 'guardian_reporting'), ('learner', 'teacher_reporting'),
                                         ('guardian', 'teacher_reporting'), ('teacher', 'tutoring'),
                                         ('teacher', 'guardian_reporting')])
def test_relationship_does_not_grant_other_purposes(role, purpose):
    assert not allowed(replace(valid(role=role), purpose=purpose))


@pytest.mark.parametrize('kind', KINDS)
def test_valid_synthetic_learner_scope_is_allowed(kind):
    assert allowed(valid(kind))


def test_guardian_and_teacher_have_explicit_reporting_scopes():
    assert allowed(replace(valid(role='guardian'), purpose='guardian_reporting'))
    assert allowed(valid(role='teacher'))
