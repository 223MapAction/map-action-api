from django.db import migrations, models


class Migration(migrations.Migration):
    """Élargit PasswordReset.code (7 -> 64) : le nouveau flux de réinitialisation
    du PIN agent de terrain (AgentRequestResetPinView) y stocke un token uuid4
    (36 caractères), trop long pour l'ancienne colonne varchar(7)."""

    dependencies = [
        ('Mapapi', '0011_user_fcm_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordreset',
            name='code',
            field=models.CharField(max_length=64),
        ),
    ]
