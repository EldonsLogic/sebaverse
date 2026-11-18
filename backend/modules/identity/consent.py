"""Canonical withdrawal fences work even if a later consent grants access again."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import ConsentRecord,Learner,Membership


@transaction.atomic
def withdraw_consent(actor,consent_id):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionError('Consent withdrawal denied')
    record=ConsentRecord.objects.select_related('relationship').get(pk=consent_id)
    learner=Learner.objects.select_for_update().get(pk=record.relationship.learner_id)
    record=ConsentRecord.objects.select_for_update().select_related('relationship').get(pk=consent_id)
    if record.relationship.guardian_id!=actor.pk or not Membership.objects.filter(actor=actor,actor__is_active=True,
            tenant=learner.tenant,role='guardian',active=True).exists():
        raise PermissionError('Consent withdrawal denied')
    if record.withdrawn_at is None:
        record.withdrawn_at=timezone.now();record.save(update_fields=['withdrawn_at'])
        Learner.objects.filter(pk=learner.pk).update(authorization_generation=F('authorization_generation')+1)
    return record
