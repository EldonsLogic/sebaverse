"""Canonical withdrawal fences work even if a later consent grants access again."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from modules.operations.models import (
    CONSENT_CLEANUP_DISPOSITION,
    CONSENT_CLEANUP_POLICY_VERSION,
    ConsentCleanupIntent,
)

from .consent_policy import qualifying_consents
from .models import ConsentRecord, Learner, Membership


def _record_cleanup_intent(learner, record, consents):
    guardian_id = record.relationship.guardian_id
    if consents.filter(relationship__guardian_id=guardian_id).exists():
        return

    # A surviving grant from another guardian limits cleanup to this uploader.
    uploader_id = guardian_id if consents.exists() else None
    ConsentCleanupIntent.objects.create(
        consent=record,
        tenant_id=learner.tenant_id,
        learner=learner,
        purpose=record.purpose,
        uploader_id=uploader_id,
        cutoff_generation=learner.authorization_generation,
        policy_version=CONSENT_CLEANUP_POLICY_VERSION,
        disposition=CONSENT_CLEANUP_DISPOSITION,
    )


@transaction.atomic
def withdraw_consent(actor, consent_id):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionError('Consent withdrawal denied')
    record = ConsentRecord.objects.select_related('relationship').get(pk=consent_id)
    # Canonical grant changes and upload allocation must share this learner lock.
    learner = Learner.objects.select_for_update().get(pk=record.relationship.learner_id)
    record = ConsentRecord.objects.select_for_update().select_related('relationship').get(
        pk=consent_id, relationship__learner_id=learner.pk,
    )
    if record.relationship.guardian_id != actor.pk or not Membership.objects.filter(
        actor=actor, actor__is_active=True, tenant_id=learner.tenant_id, role='guardian', active=True,
    ).exists():
        raise PermissionError('Consent withdrawal denied')
    if record.withdrawn_at is not None:
        return record

    now = timezone.now()
    consents = qualifying_consents(learner, record.purpose, now) if record.purpose == 'tutoring' else None
    was_qualifying = consents is not None and consents.filter(pk=record.pk).exists()
    record.withdrawn_at = now
    record.save(update_fields=['withdrawn_at'])
    Learner.objects.filter(pk=learner.pk).update(authorization_generation=F('authorization_generation') + 1)
    if was_qualifying:
        _record_cleanup_intent(learner, record, consents)
    return record
