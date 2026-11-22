from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [('operations', '0005_consent_cleanup_intent')]

    operations = [
        migrations.AddField(
            model_name='consentcleanupintent', name='status',
            field=models.CharField(default='pending', max_length=16),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='due_at', field=models.DateTimeField(default=timezone.now),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='lease_until', field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='fence', field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='cursor', field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='attempts', field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='consentcleanupintent', name='failure_code', field=models.CharField(blank=True, max_length=24),
        ),
        migrations.AddConstraint(
            model_name='consentcleanupintent',
            constraint=models.CheckConstraint(
                condition=models.Q(status__in=['pending', 'complete', 'blocked']),
                name='operations_consent_cleanup_state',
            ),
        ),
        migrations.AddConstraint(
            model_name='consentcleanupintent',
            constraint=models.CheckConstraint(
                condition=models.Q(attempts__lte=3), name='operations_consent_cleanup_attempt_cap',
            ),
        ),
        migrations.AddIndex(
            model_name='consentcleanupintent',
            index=models.Index(fields=['status', 'due_at', 'id'], name='operations_cleanup_due'),
        ),
    ]
