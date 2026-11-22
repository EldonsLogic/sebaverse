"""Bounded local consumer for committed, server-derived consent cleanup intents."""
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from modules.operations.models import (
    CONSENT_CLEANUP_DISPOSITION,
    CONSENT_CLEANUP_POLICY_VERSION,
    ConsentCleanupIntent,
)

from .models import Upload
from .service import locked


LEASE_DURATION = timedelta(minutes=1)
RETRY_DELAYS = (timedelta(seconds=1), timedelta(seconds=2))
MAX_ATTEMPTS = len(RETRY_DELAYS) + 1
MAX_BATCH = 100


def _require_autocommit():
    if not transaction.get_autocommit():
        raise RuntimeError('Consent cleanup requires autocommit')


@transaction.atomic
def _claim_intent():
    now = timezone.now()
    intent = (
        ConsentCleanupIntent.objects.select_for_update(skip_locked=True)
        .filter(status='pending', due_at__lte=now)
        .filter(Q(lease_until__isnull=True) | Q(lease_until__lte=now))
        .order_by('due_at', 'pk')
        .first()
    )
    if intent is not None:
        intent.lease_until = now + LEASE_DURATION
        intent.fence += 1
        intent.save(update_fields=['lease_until', 'fence'])
    return intent


def _lease_rows(intent):
    return ConsentCleanupIntent.objects.filter(
        pk=intent.pk, status='pending', fence=intent.fence,
        consent_id=intent.consent_id, tenant_id=intent.tenant_id, learner_id=intent.learner_id,
        purpose=intent.purpose, uploader_id=intent.uploader_id, cutoff_generation=intent.cutoff_generation,
        policy_version=intent.policy_version, disposition=intent.disposition,
    )


def _has_lease(intent):
    return _lease_rows(intent).filter(lease_until__gt=timezone.now()).exists()


def _hold_lease(intent):
    # Check expiry after acquiring the row lock in case another transaction held it.
    lease_until = _lease_rows(intent).select_for_update().values_list('lease_until', flat=True).first()
    return lease_until is not None and lease_until > timezone.now()


def _valid_intent(intent):
    consent, learner = intent.consent, intent.learner
    return (
        intent.policy_version == CONSENT_CLEANUP_POLICY_VERSION
        and intent.disposition == CONSENT_CLEANUP_DISPOSITION
        and intent.purpose == consent.purpose == 'tutoring'
        and consent.withdrawn_at is not None
        and consent.granted_at <= consent.withdrawn_at < consent.expires_at
        and learner.tenant_id == intent.tenant_id
        and consent.relationship.learner_id == intent.learner_id
        and intent.uploader_id in (None, consent.relationship.guardian_id)
        and 0 <= intent.cutoff_generation < learner.authorization_generation
    )


def _candidates(intent):
    # Include disputed bindings for inspection so drift cannot hide unresolved files.
    candidates = Upload.objects.filter(
        Q(resource__learner_id=intent.learner_id)
        | Q(quota__learner_id=intent.learner_id)
        | Q(scope__learner=str(intent.learner_id)),
        Q(resource__purpose=intent.purpose) | Q(scope__purpose=intent.purpose),
        authorization_generation__lte=intent.cutoff_generation,
        purge_confirmed=False,
    )
    if intent.uploader_id is not None:
        candidates = candidates.filter(actor_id=intent.uploader_id)
    return candidates


def _matches_target(intent, quota, upload):
    resource = upload.resource
    saved = upload.scope
    # Allocation only creates uploads for files. Its saved scope is the original
    # binding even if the resource's kind, purpose or edition now denies access.
    return (
        quota.pk == upload.quota_id
        and quota.learner_id == resource.learner_id == intent.learner_id
        and quota.course_id == resource.course_id
        and resource.learner.tenant_id == resource.course.tenant_id == intent.tenant_id
        and isinstance(saved, dict)
        and saved.get('learner') == str(intent.learner_id)
        and saved.get('course') == str(quota.course_id)
        and saved.get('purpose') == intent.purpose
        and upload.authorization_generation <= intent.cutoff_generation
        and (intent.uploader_id is None or upload.actor_id == intent.uploader_id)
    )


def _charges_match(quota, upload):
    used = upload.stored_bytes + upload.manifest_bytes
    if upload.status == 'deleted':
        return used == upload.held_bytes == 0
    return (
        upload.stored_bytes <= upload.declared_bytes
        and upload.held_bytes <= upload.declared_bytes
        and quota.used_bytes >= used
        and quota.reserved_bytes >= upload.held_bytes
    )


def _prepare_target(intent, upload_id):
    # Lock order is quota -> upload -> learner -> intent. Intent-only operations
    # release their locks before any ingestion lock is acquired.
    with transaction.atomic():
        quota, upload = locked(upload_id)
        if not _hold_lease(intent):
            return None, None
        if not _matches_target(intent, quota, upload) or not _charges_match(quota, upload):
            return 'integrity_error', None
        if upload.purge_confirmed:
            return '', None
        if upload.status not in ('withdrawn', 'deleted'):
            upload.status = 'withdrawn'
            upload.generation += 1
            upload.save(update_fields=['status', 'generation'])
        if upload.writer_active:
            return 'writer_active', None
        return '', upload.generation


def _settle_target(intent, upload_id, generation):
    with transaction.atomic():
        quota, upload = locked(upload_id)
        if not _hold_lease(intent):
            return None
        if (not _matches_target(intent, quota, upload) or not _charges_match(quota, upload)
                or upload.status not in ('withdrawn', 'deleted') or upload.generation != generation):
            return 'integrity_error'
        if upload.writer_active:
            return 'writer_active'
        if upload.purge_confirmed:
            return ''

        # The lifecycle locks serialize accounting with concurrent purge attempts.
        # A legacy deleted row already gave up its charges and only needs confirmation.
        if upload.status == 'withdrawn':
            quota.used_bytes -= upload.stored_bytes + upload.manifest_bytes
            quota.reserved_bytes -= upload.held_bytes
            quota.save(update_fields=['used_bytes', 'reserved_bytes'])
            upload.stored_bytes = upload.manifest_bytes = upload.held_bytes = 0
            upload.status = 'deleted'
        upload.purge_confirmed = True
        upload.save(update_fields=['stored_bytes', 'manifest_bytes', 'held_bytes', 'status', 'purge_confirmed'])
    return ''


def _process_target(intent, upload_id, store):
    try:
        outcome, generation = _prepare_target(intent, upload_id)
        if generation is None:
            return outcome
        # The target is irreversibly fenced, so an overlapping purge after lease
        # expiry is safe. Storage stays outside both target and intent locks.
        if not _has_lease(intent):
            return None
        try:
            confirmed = store.purge_confirmed(str(upload_id))
        except OSError:
            return 'purge_failed'
        if confirmed is not True:
            return 'purge_failed'
        return _settle_target(intent, upload_id, generation)
    except ObjectDoesNotExist:
        return 'integrity_error'


def _finish_batch(intent, *, cursor=None, failure_code='', more=False, unresolved=False, invalid=False):
    updates = dict(lease_until=None, cursor=cursor, failure_code=failure_code)
    retry_delay = timedelta(0)
    if invalid:
        updates['status'] = 'blocked'
    elif not more:
        updates['cursor'] = None
        if not unresolved:
            updates.update(status='complete', failure_code='')
        else:
            attempts = intent.attempts + 1
            updates.update(attempts=attempts, failure_code=failure_code or 'retry_pending')
            if attempts >= MAX_ATTEMPTS:
                updates['status'] = 'blocked'
            else:
                retry_delay = RETRY_DELAYS[attempts - 1]

    with transaction.atomic():
        if not _hold_lease(intent):
            return None
        updates['due_at'] = timezone.now() + retry_delay
        _lease_rows(intent).update(**updates)
    for field, value in updates.items():
        setattr(intent, field, value)
    return intent


def run_batch(store, limit=25):
    """Claim one intent and examine at most ``limit`` targets; no caller-supplied scope."""
    _require_autocommit()
    if type(limit) is not int or not 1 <= limit <= MAX_BATCH:
        raise ValueError('Invalid consent cleanup batch limit')
    intent = _claim_intent()
    if intent is None:
        return None
    if not _valid_intent(intent):
        return _finish_batch(intent, invalid=True, failure_code='integrity_error')

    candidates = _candidates(intent)
    cursor, failure_code = intent.cursor, intent.failure_code
    page = candidates.filter(pk__gt=cursor) if cursor is not None else candidates
    for upload_id in list(page.order_by('pk').values_list('pk', flat=True)[:limit]):
        outcome = _process_target(intent, upload_id, store)
        if outcome is None:
            return None
        cursor = upload_id
        failure_code = outcome or failure_code

    more = cursor is not None and candidates.filter(pk__gt=cursor).exists()
    # At the end of each pass, check all unresolved rows, including those behind the cursor.
    return _finish_batch(
        intent, cursor=cursor, failure_code=failure_code, more=more,
        unresolved=not more and candidates.exists(),
    )


def retry_blocked_intent(intent_id):
    """Internal operator replay after reconciliation, with the original scope intact."""
    _require_autocommit()
    return bool(ConsentCleanupIntent.objects.filter(pk=intent_id, status='blocked').update(
        status='pending', attempts=0, lease_until=None, cursor=None, due_at=timezone.now(), failure_code='',
    ))
