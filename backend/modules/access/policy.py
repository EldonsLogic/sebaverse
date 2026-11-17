"""Pure decision over server-derived facts; not a client request schema."""
from dataclasses import dataclass

KINDS = frozenset({'material', 'file', 'job', 'stream', 'export', 'vector', 'course', 'edition'})
PURPOSES = {'learner': {'tutoring'}, 'guardian': {'tutoring', 'guardian_reporting'},
            'teacher': {'teacher_reporting'}}


@dataclass(frozen=True)
class Scope:
    actor_active: bool
    member_active: bool
    role: str
    tenant_matches: bool
    learner_active: bool
    relationship_valid: bool
    consent_valid: bool
    enrollment_valid: bool
    entitlement_valid: bool
    course_active: bool
    edition_active: bool
    resource_active: bool
    version_matches: bool
    purpose: str
    kind: str


def allowed(scope):
    checks = ('actor_active', 'member_active', 'tenant_matches', 'learner_active',
              'relationship_valid', 'consent_valid', 'enrollment_valid', 'entitlement_valid',
              'course_active', 'edition_active', 'resource_active', 'version_matches')
    return (all(getattr(scope, field) is True for field in checks)
            and scope.kind in KINDS and scope.purpose in PURPOSES.get(scope.role, set()))
