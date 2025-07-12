from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Count, Q
from .models import PlayerProgress, Question, SubmissionHistory
import json

class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("leaderboard", self.channel_name)
        await self.accept()
        await self.send_leaderboard()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("leaderboard", self.channel_name)
    
    async def receive(self, text_data):
        pass  # We don't expect to receive messages from clients
    
    async def leaderboard_update(self, event):
        await self.send_leaderboard()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'request_update':
            await self.send_leaderboard(data.get('sort', {'column': 'score', 'direction': 'desc'}))

    @database_sync_to_async
    def get_leaderboard_data(self, sort_params=None):
        from django.db.models import F, Max
        from django.utils import timezone
        from datetime import timedelta

        # Base query with annotations and anti-manipulation checks
        players = PlayerProgress.objects.annotate(
            total_questions=Count('completed_questions'),
            correct_attempts=Count('user__submissionhistory', 
                filter=Q(user__submissionhistory__is_correct=True) & 
                       ~Q(user__submissionhistory__submission_time__gt=F('user__submissionhistory__submission_time') + timedelta(seconds=2))
            ),
            total_attempts=Count('user__submissionhistory'),
            last_activity=Max('user__activitylog__timestamp'),
            time_taken=ExpressionWrapper(F('finish_time') - F('start_time'), output_field=DurationField())
        ).filter(
            Q(finish_time__isnull=False)  # Only show completed players
        ).order_by('-score', 'time_taken')  # Sort by score desc, then time taken asc

        # No need for additional sorting since it's handled in the query

        total_questions = Question.objects.count()
        
        return [{
            'username': player.user.username,
            'score': player.score,
            'completed': player.finish_time is not None,
            'duration': str(player.time_taken).split('.')[0] if player.time_taken else 'In Progress',
            'completed_questions': player.completed_questions.count(),
            'total_questions': total_questions
        } for player in players[:10]]
    
    async def send_leaderboard(self):
        from django.core.cache import cache
        from django.utils import timezone
        import hashlib

        # Generate cache key based on current time window (5 minute intervals)
        time_window = int(timezone.now().timestamp() / 300)  # 5 minutes
        cache_key = f'leaderboard_data_{time_window}'
        
        # Try to get cached data
        leaderboard_data = cache.get(cache_key)
        if not leaderboard_data:
            leaderboard_data = await self.get_leaderboard_data()
            cache.set(cache_key, leaderboard_data, 300)  # Cache for 5 minutes

        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'leaderboard': leaderboard_data
        }))