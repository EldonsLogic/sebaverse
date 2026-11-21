"""Derive live scope from persisted records; never accept role/paid/consent claims."""
from django.utils import timezone
from modules.identity.models import Membership, GuardianRelationship
from modules.identity.consent_policy import qualifying_consents
from .models import ScopedResource, Enrollment, Entitlement, TeacherAssignment
from .policy import Scope, allowed


def authorized_resource(actor, resource_id):
    if not actor.is_authenticated or not actor.is_active:
        return None
    resource = ScopedResource.objects.select_related('learner__tenant', 'learner__actor', 'course__tenant').filter(pk=resource_id).first()
    if resource is None:
        return None
    learner, course = resource.learner, resource.course
    now = timezone.now()
    member = Membership.objects.filter(actor_id=actor.pk, tenant_id=learner.tenant_id, active=True, actor__is_active=True).first()
    role = member.role if member else ''
    relationship = False
    if role == 'learner':
        relationship = learner.actor_id == actor.pk
    elif role == 'guardian':
        relationship = GuardianRelationship.objects.filter(guardian_id=actor.pk, learner=learner,
            verified_at__lte=now, revoked_at__isnull=True).exclude(verification_ref='').exists()
    elif role == 'teacher':
        relationship = TeacherAssignment.objects.filter(actor_id=actor.pk, learner=learner, course=course, active=True).exists()
    consents = qualifying_consents(learner, resource.purpose, now)
    # A guardian may not borrow another guardian's consent to their own reporting.
    if role == 'guardian':
        consents = consents.filter(relationship__guardian_id=actor.pk)
    consent_valid = consents.exists()
    enrollment = Enrollment.objects.filter(learner=learner, course=course, active=True).first()
    entitlement_valid = bool(enrollment and Entitlement.objects.filter(enrollment=enrollment,
        purpose=resource.purpose, starts_at__lte=now, expires_at__gt=now,
        revoked_at__isnull=True, remaining_units__gt=0).exists())
    facts = Scope(actor_active=actor.is_active, member_active=member is not None, role=role,
        tenant_matches=(learner.tenant_id == course.tenant_id and learner.tenant.active and course.tenant.active),
        learner_active=learner.active and learner.actor.is_active, relationship_valid=relationship,
        consent_valid=consent_valid, enrollment_valid=enrollment is not None,
        entitlement_valid=entitlement_valid, course_active=course.active, edition_active=course.edition_active,
        resource_active=resource.active, version_matches=(resource.edition_id == course.edition_id and
            resource.edition_version == course.edition_version), purpose=resource.purpose, kind=resource.kind)
    return resource if allowed(facts) else None
