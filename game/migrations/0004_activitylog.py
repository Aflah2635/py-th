# Generated by Django 5.2.3 on 2025-06-23 09:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_question_audio_question_video'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('login', 'Login'), ('logout', 'Logout'), ('register', 'Register'), ('clue_solved', 'Clue Solved'), ('hint_used', 'Hint Used'), ('wrong_answer', 'Wrong Answer'), ('game_completed', 'Game Completed')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('meta_info', models.TextField(blank=True, help_text='Additional information about the activity', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Activity Log',
                'verbose_name_plural': 'Activity Logs',
                'ordering': ['-timestamp'],
            },
        ),
    ]
