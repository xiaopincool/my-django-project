from django.db import migrations, models


def to_program(apps, schema_editor):
    EngUser = apps.get_model('users', 'EngUser')
    EngUser.objects.filter(role='expert').update(role='program')


def to_expert(apps, schema_editor):
    EngUser = apps.get_model('users', 'EngUser')
    EngUser.objects.filter(role='program').update(role='expert')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_enguser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enguser',
            name='role',
            field=models.CharField(
                choices=[('admin', '管理员'), ('teacher', '任课教师'), ('program', '专业负责人')],
                default='teacher',
                max_length=20,
                verbose_name='角色',
            ),
        ),
        migrations.RunPython(to_program, to_expert),
    ]
