from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accreditation', '0005_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='average_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='平均分'),
        ),
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='class_name',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='班级'),
        ),
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='college_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='学院'),
        ),
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='grade_name',
            field=models.CharField(blank=True, default='', max_length=30, verbose_name='年级'),
        ),
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='major_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='专业'),
        ),
        migrations.AddField(
            model_name='courseattainmentrecord',
            name='total_score',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=7, verbose_name='总分'),
        ),
    ]
