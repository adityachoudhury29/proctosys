# Generated by Django 5.0.4 on 2024-05-26 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proctor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='unfair_means',
            field=models.BooleanField(default=False),
        ),
    ]
