import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q,F


class UploadQuota(models.Model):
    learner=models.ForeignKey('identity.Learner',on_delete=models.PROTECT)
    course=models.ForeignKey('access.Course',on_delete=models.PROTECT)
    limit_bytes=models.PositiveBigIntegerField()
    used_bytes=models.PositiveBigIntegerField(default=0)
    reserved_bytes=models.PositiveBigIntegerField(default=0)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['learner','course'],name='ingestion_unique_quota'),
                     models.CheckConstraint(condition=Q(limit_bytes__gte=F('used_bytes')+F('reserved_bytes')),name='ingestion_quota_conservation')]


class ReviewGrant(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    learner=models.ForeignKey('identity.Learner',on_delete=models.PROTECT)
    course=models.ForeignKey('access.Course',on_delete=models.PROTECT)
    active=models.BooleanField(default=False)
    rights=models.BooleanField(default=False)
    extraction=models.BooleanField(default=False)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['actor','learner','course'],name='ingestion_unique_reviewer')]


class Upload(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    resource=models.ForeignKey('access.ScopedResource',on_delete=models.PROTECT)
    quota=models.ForeignKey(UploadQuota,on_delete=models.PROTECT)
    command_key=models.CharField(max_length=96)
    request_digest=models.CharField(max_length=64)
    scope=models.JSONField()
    authorization_generation=models.PositiveIntegerField()
    generation=models.PositiveIntegerField(default=1)
    declared_bytes=models.PositiveIntegerField()
    held_bytes=models.PositiveIntegerField(default=0)
    writer_active=models.BooleanField(default=False)
    writer_binding=models.JSONField(null=True)
    attempts=models.PositiveIntegerField(default=0)
    stored_bytes=models.PositiveIntegerField(default=0)
    manifest_bytes=models.PositiveIntegerField(default=0)
    purge_confirmed=models.BooleanField(default=False)
    media_type=models.CharField(max_length=32)
    rights_claim=models.CharField(max_length=2000)
    status=models.CharField(max_length=24,default='awaiting_bytes')
    source_sha256=models.CharField(max_length=64,blank=True)
    parser_id=models.CharField(max_length=96,blank=True)
    scan_id=models.CharField(max_length=96,blank=True)
    dispatch_id=models.UUIDField(null=True)
    manifest_sha256=models.CharField(max_length=64,blank=True)
    rights_evidence=models.CharField(max_length=96,blank=True)
    rights_expires=models.DateTimeField(null=True)
    rights_reviewer=models.ForeignKey(ReviewGrant,on_delete=models.PROTECT,null=True,related_name='+')
    extraction_reviewer=models.ForeignKey(ReviewGrant,on_delete=models.PROTECT,null=True,related_name='+')
    failure_code=models.CharField(max_length=32,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['actor','command_key'],name='ingestion_idempotent_upload'),
                     models.CheckConstraint(condition=Q(generation__gte=1),name='ingestion_positive_generation'),
                     models.CheckConstraint(condition=Q(attempts__lte=3),name='ingestion_attempt_cap'),
                     models.CheckConstraint(condition=Q(status__in=['awaiting_bytes','receiving','quarantined','processing','needs_review','private_ready','failed','withdrawn','deleted']),name='ingestion_known_state'),
                     models.CheckConstraint(
                         condition=Q(writer_binding__isnull=True) | Q(
                             writer_active=True, status__in=['receiving', 'withdrawn'],
                         ),
                         name='ingestion_writer_binding_active',
                     ),
                     models.CheckConstraint(
                         condition=Q(purge_confirmed=False) | Q(
                             status='deleted', writer_active=False, held_bytes=0, stored_bytes=0, manifest_bytes=0,
                         ),
                         name='ingestion_confirmed_purge_terminal',
                     )]
