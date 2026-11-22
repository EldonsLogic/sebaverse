from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('ingestion', '0005_upload_manifest_bytes')]

    operations = [
        migrations.AddField(
            model_name='upload', name='purge_confirmed', field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='upload',
            constraint=models.CheckConstraint(
                condition=models.Q(purge_confirmed=False) | models.Q(
                    status='deleted', writer_active=False, held_bytes=0, stored_bytes=0, manifest_bytes=0,
                ),
                name='ingestion_confirmed_purge_terminal',
            ),
        ),
    ]
