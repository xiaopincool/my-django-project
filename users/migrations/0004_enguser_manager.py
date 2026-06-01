from django.db import migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_program_role'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='enguser',
            managers=[
                ('objects', users.models.EngUserManager()),
            ],
        ),
    ]
