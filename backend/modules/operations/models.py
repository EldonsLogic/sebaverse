import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q


CONSENT_CLEANUP_POLICY_VERSION = 'effective-loss-v1'
CONSENT_CLEANUP_DISPOSITION = 'full_purge'


class ConsentCleanupIntent(models.Model):
    """Write-once scope for an eligible withdrawal, with an inclusive generation cutoff."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consent = models.OneToOneField('identity.ConsentRecord', on_delete=models.PROTECT, editable=False)
    tenant = models.ForeignKey('identity.Tenant', on_delete=models.PROTECT, editable=False)
    learner = models.ForeignKey('identity.Learner', on_delete=models.PROTECT, editable=False)
    purpose = models.CharField(max_length=24, editable=False)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, editable=False)
    cutoff_generation = models.PositiveIntegerField(editable=False)
    policy_version = models.CharField(max_length=32, editable=False)
    disposition = models.CharField(max_length=24, editable=False)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=Q(
                purpose='tutoring', policy_version=CONSENT_CLEANUP_POLICY_VERSION,
                disposition=CONSENT_CLEANUP_DISPOSITION,
            ),
            name='operations_consent_cleanup_policy',
        )]


class Job(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    resource=models.ForeignKey('access.ScopedResource',on_delete=models.PROTECT)
    budget=models.ForeignKey('usage.Budget',on_delete=models.PROTECT)
    command_key=models.CharField(max_length=96)
    scope_generation=models.PositiveIntegerField(default=0)
    scope=models.JSONField(default=dict)
    request_digest=models.CharField(max_length=64)
    request=models.JSONField()
    reserved_units=models.PositiveIntegerField()
    status=models.CharField(max_length=20,default='queued')
    fence=models.PositiveIntegerField(default=0)
    attempts=models.PositiveIntegerField(default=0)
    lease_until=models.DateTimeField(null=True)
    due_at=models.DateTimeField()
    deadline=models.DateTimeField()
    cancelled=models.BooleanField(default=False)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['actor','command_key'],name='operations_idempotent_command'),
                     models.CheckConstraint(condition=Q(status__in=['queued','running','waiting_retry','succeeded','failed','cancelled','unknown']),name='operations_known_state'),
                     models.CheckConstraint(condition=Q(attempts__lte=3),name='operations_attempt_cap')]


class Attempt(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    job=models.ForeignKey(Job,on_delete=models.PROTECT)
    fence=models.PositiveIntegerField()
    provider=models.CharField(max_length=24)
    state=models.CharField(max_length=20,default='started')
    error_code=models.CharField(max_length=24,blank=True)
    receipt=models.JSONField(null=True)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['job','fence'],name='operations_one_attempt_per_fence')]


class UsageReceipt(models.Model):
    attempt=models.OneToOneField(Attempt,on_delete=models.PROTECT)
    provider=models.CharField(max_length=24)
    request_id=models.CharField(max_length=96)
    units=models.JSONField()

    class Meta:
        constraints=[models.UniqueConstraint(fields=['provider','request_id'],name='operations_unique_provider_receipt')]
