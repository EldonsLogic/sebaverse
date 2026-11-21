import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('identity', '0002_learner_authorization_generation'),
        ('operations', '0004_job_scope'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsentCleanupIntent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('consent', models.OneToOneField(
                    editable=False, on_delete=django.db.models.deletion.PROTECT, to='identity.consentrecord',
                )),
                ('tenant', models.ForeignKey(
                    editable=False, on_delete=django.db.models.deletion.PROTECT, to='identity.tenant',
                )),
                ('learner', models.ForeignKey(
                    editable=False, on_delete=django.db.models.deletion.PROTECT, to='identity.learner',
                )),
                ('purpose', models.CharField(editable=False, max_length=24)),
                ('uploader', models.ForeignKey(
                    editable=False, null=True, on_delete=django.db.models.deletion.PROTECT,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('cutoff_generation', models.PositiveIntegerField(editable=False)),
                ('policy_version', models.CharField(editable=False, max_length=32)),
                ('disposition', models.CharField(editable=False, max_length=24)),
            ],
            options={
                'constraints': [models.CheckConstraint(
                    condition=models.Q(disposition='full_purge', policy_version='effective-loss-v1', purpose='tutoring'),
                    name='operations_consent_cleanup_policy',
                )],
            },
        ),
    ]
