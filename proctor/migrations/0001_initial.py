# Generated by Django 5.0.4 on 2024-05-10 18:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=1000)),
                ('answer', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('student', 'student'), ('proctor', 'proctor')], max_length=50)),
                ('profile', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(default='NOTE: Do not change tab or window during exam duration, as Screen visibility change will immediately terminate the examination and authorities wont be liable for it.')),
                ('duration', models.IntegerField(help_text='Duration of exam in minutes')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('status', models.BooleanField(default=False)),
                ('proctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proctored_exams', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_exams', to=settings.AUTH_USER_MODEL)),
                ('questions', models.ManyToManyField(related_name='exams', to='proctor.question')),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=1000)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_response', to='proctor.exam')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_response', to='proctor.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_response', to='proctor.profile')),
            ],
        ),
    ]
