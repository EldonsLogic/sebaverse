import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from .policy import KINDS


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('identity.Tenant', on_delete=models.PROTECT)
    edition_id = models.CharField(max_length=96)
    edition_version = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    edition_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(edition_version__gte=1), name='access_positive_edition')]


class Enrollment(models.Model):
    learner = models.ForeignKey('identity.Learner', on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['learner', 'course'], name='access_unique_enrollment')]


class Entitlement(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=24)
    starts_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)
    remaining_units = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(expires_at__gt=models.F('starts_at')), name='access_entitlement_window')]


class TeacherAssignment(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    learner = models.ForeignKey('identity.Learner', on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['actor', 'learner', 'course'], name='access_unique_teacher_assignment')]


class ScopedResource(models.Model):
    """Scope anchor only; never stores content, keys, transcript or credentials."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner = models.ForeignKey('identity.Learner', on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    kind = models.CharField(max_length=16, choices=[(x, x) for x in sorted(KINDS)])
    purpose = models.CharField(max_length=24)
    edition_id = models.CharField(max_length=96)
    edition_version = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=Q(kind__in=sorted(KINDS)), name='access_known_resource_kind'),
                       models.CheckConstraint(condition=Q(edition_version__gte=1), name='access_resource_positive_version')]
