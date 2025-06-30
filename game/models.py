from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    answer = models.CharField(max_length=200)
    points = models.IntegerField(default=10)
    order = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='questions/', null=True, blank=True)
    audio = models.FileField(upload_to='questions/audio/', null=True, blank=True)
    video = models.FileField(upload_to='questions/video/', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

class Hint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='hints')
    content = models.TextField()
    penalty_points = models.IntegerField(default=5)

    def __str__(self):
        return f'Hint for {self.question.title}'

class QuestionProgress(models.Model):
    player = models.ForeignKey('PlayerProgress', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    completion_time = models.DateTimeField(null=True, blank=True)
    score_earned = models.IntegerField(default=0)
    time_taken = models.DurationField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.completion_time and self.start_time:
            self.time_taken = self.completion_time - self.start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.player.user.username} - {self.question.title}'

class HintUsage(models.Model):
    question_progress = models.ForeignKey(QuestionProgress, on_delete=models.CASCADE)
    hint = models.ForeignKey(Hint, on_delete=models.CASCADE)
    used_time = models.DateTimeField(auto_now_add=True)
    points_deducted = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.question_progress.player.user.username} used hint for {self.question_progress.question.title}'

class PlayerProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField(default=0)
    completed_questions = models.ManyToManyField(Question, related_name='completed_by', blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    finish_time = models.DateTimeField(null=True, blank=True)
    total_hints_used = models.IntegerField(default=0)
    total_time_spent = models.DurationField(default=timedelta)

    def __str__(self):
        return f'{self.user.username} - Score: {self.score}'

class SubmissionHistory(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.player.username} - {self.question.title} - {"Correct" if self.is_correct else "Incorrect"}'

    class Meta:
        verbose_name_plural = 'Submission histories'
        ordering = ['-submission_time']
