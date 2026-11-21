"""Build the live consent predicate for access and withdrawal decisions."""

from .models import ConsentRecord, Membership


def qualifying_consents(learner, purpose, now):
    guardian_ids = Membership.objects.filter(
        tenant_id=learner.tenant_id, role='guardian', active=True,
    ).values('actor_id')
    return ConsentRecord.objects.filter(
        relationship__learner=learner,
        relationship__guardian_id__in=guardian_ids,
        relationship__guardian__is_active=True,
        relationship__verified_at__lte=now,
        relationship__revoked_at__isnull=True,
        purpose=purpose,
        granted_at__lte=now,
        expires_at__gt=now,
        withdrawn_at__isnull=True,
    ).exclude(relationship__verification_ref='').exclude(notice_version='').exclude(
        notice_locale='',
    ).exclude(evidence_ref='')
