import uuid
from django.db import models
from django.db.models import Q,F


class Budget(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    learner=models.ForeignKey('identity.Learner',on_delete=models.PROTECT)
    course=models.ForeignKey('access.Course',on_delete=models.PROTECT)
    purpose=models.CharField(max_length=24)
    limit=models.PositiveIntegerField()
    spent=models.PositiveIntegerField(default=0)
    reserved=models.PositiveIntegerField(default=0)
    blocked=models.BooleanField(default=False)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['learner','course','purpose'],name='usage_unique_budget'),
                     models.CheckConstraint(condition=Q(limit__gte=F('spent')+F('reserved')),name='usage_budget_conservation')]
