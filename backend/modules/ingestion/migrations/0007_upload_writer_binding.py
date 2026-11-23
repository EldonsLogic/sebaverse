from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('ingestion', '0006_upload_purge_confirmed')]

    operations = [
        migrations.AddField(
            model_name='upload', name='writer_binding', field=models.JSONField(null=True),
        ),
        migrations.AddConstraint(
            model_name='upload',
            constraint=models.CheckConstraint(
                condition=models.Q(writer_binding__isnull=True) | models.Q(
                    writer_active=True, status__in=['receiving', 'withdrawn'],
                ),
                name='ingestion_writer_binding_active',
            ),
        ),
    ]
