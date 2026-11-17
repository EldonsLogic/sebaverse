"""Consent is mandatory for every supported resource and caller purpose."""
from dataclasses import replace
import pytest
from modules.access.policy import allowed
from tests.authorization.test_policy import valid, KINDS


@pytest.mark.parametrize('role,purpose', [('learner','tutoring'), ('guardian','tutoring'),
                                         ('guardian','guardian_reporting'), ('teacher','teacher_reporting')])
@pytest.mark.parametrize('kind', KINDS)
def test_withdrawn_or_unverified_consent_never_grants_scope(role, purpose, kind):
    assert not allowed(replace(valid(kind, role), purpose=purpose, consent_valid=False))
