# Generated by Django 5.0.4 on 2024-05-27 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proctor', '0002_exam_unfair_means'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('student', 'student'), ('proctor', 'proctor'), ('admin', 'admin')], max_length=50),
        ),
    ]