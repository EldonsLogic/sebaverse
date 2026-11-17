import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q


class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)


class Membership(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    role = models.CharField(max_length=16, choices=[(x, x) for x in ['learner', 'guardian', 'teacher', 'staff']])
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['tenant', 'actor'], name='identity_unique_member'),
                       models.CheckConstraint(condition=Q(role__in=['learner', 'guardian', 'teacher', 'staff']), name='identity_known_role')]


class Learner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['tenant', 'actor'], name='identity_unique_learner')]


class GuardianRelationship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guardian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    learner = models.ForeignKey(Learner, on_delete=models.PROTECT)
    verified_at = models.DateTimeField(null=True)
    verification_ref = models.CharField(max_length=96, blank=True)
    revoked_at = models.DateTimeField(null=True)


class ConsentRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relationship = models.ForeignKey(GuardianRelationship, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=24, choices=[(x, x) for x in ['tutoring', 'guardian_reporting', 'teacher_reporting']])
    notice_version = models.CharField(max_length=96)
    notice_locale = models.CharField(max_length=16)
    evidence_ref = models.CharField(max_length=96)
    granted_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    withdrawn_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(expires_at__gt=models.F('granted_at')), name='identity_consent_window'),
                       models.CheckConstraint(condition=Q(purpose__in=['tutoring', 'guardian_reporting', 'teacher_reporting']), name='identity_known_purpose')]
