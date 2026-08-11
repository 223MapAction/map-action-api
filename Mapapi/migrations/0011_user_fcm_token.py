from django.db import migrations, models


class Migration(migrations.Migration):
    """Ajoute User.fcm_token : token Firebase Cloud Messaging de l'appareil de
    l'utilisateur, utilisé pour l'envoi de notifications push."""

    dependencies = [
        ('Mapapi', '0010_incidentassignment_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcm_token',
            field=models.CharField(blank=True, help_text="Token Firebase Cloud Messaging de l'appareil de l'utilisateur.", max_length=255, null=True),
        ),
    ]
