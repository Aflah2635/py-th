from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Question(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    answer = models.CharField(max_length=200)
    points = models.IntegerField(default=10)
    order = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order}. {self.title}"

    class Meta:
        ordering = ['order']

class Hint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='hints')
    content = models.TextField()
    penalty_points = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hint for {self.question.title}"

class PlayerProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.IntegerField(default=0)
    hints_used = models.ManyToManyField(Hint, blank=True)
    last_submission = models.DateTimeField(null=True, blank=True)
    completed_questions = models.ManyToManyField(Question, related_name='completed_by', blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    finish_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Progress"

    def is_game_completed(self):
        return self.finish_time is not None

    def calculate_rank(self):
        higher_scores = PlayerProgress.objects.filter(
            score__gt=self.score
        ).count()
        return higher_scores + 1

class SubmissionHistory(models.Model):
    player = models.ForeignKey(PlayerProgress, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    submitted_answer = models.CharField(max_length=200)
    is_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username}'s submission for {self.question.title}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = 'Submission histories'


from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"
