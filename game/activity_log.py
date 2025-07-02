from django.db import models
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Register'),
        ('clue_solved', 'Clue Solved'),
        ('hint_used', 'Hint Used'),
        ('wrong_answer', 'Wrong Answer'),
        ('game_completed', 'Game Completed')
    ]

    class Meta:
        indexes = [
            models.Index(fields=['activity_type', '-timestamp']),
            models.Index(fields=['user', '-timestamp'])
        ]
        permissions = [
            ('view_clue_completions', 'Can view clue completion logs')
        ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta_info = models.TextField(blank=True, null=True, help_text='Additional information about the activity')

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}'

async def log_activity(user, activity_type, meta_info=None):
    await sync_to_async(ActivityLog.objects.create)(
        user=user,
        activity_type=activity_type,
        meta_info=meta_info or ""
    )