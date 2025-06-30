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
        if not sort_params:
            sort_params = {'column': 'score', 'direction': 'desc'}

        # Base query with annotations
        players = PlayerProgress.objects.annotate(
            total_questions=Count('completed_questions'),
            correct_attempts=Count('user__submissionhistory', filter=Q(user__submissionhistory__is_correct=True)),
            total_attempts=Count('user__submissionhistory')
        )

        # Apply sorting
        sort_prefix = '-' if sort_params['direction'] == 'desc' else ''
        if sort_params['column'] == 'accuracy':
            players = sorted(
                players,
                key=lambda p: (p.correct_attempts / p.total_attempts if p.total_attempts > 0 else 0),
                reverse=(sort_params['direction'] == 'desc')
            )
        elif sort_params['column'] == 'progress':
            players = players.order_by(f'{sort_prefix}total_questions')
        elif sort_params['column'] == 'time':
            players = sorted(
                players,
                key=lambda p: (p.finish_time - p.start_time) if p.finish_time else float('inf'),
                reverse=(sort_params['direction'] == 'desc')
            )
        else:  # Default to score
            players = players.order_by(f'{sort_prefix}score')

        total_questions = Question.objects.count()
        
        return [{
            'username': player.user.username,
            'score': player.score,
            'completed': player.finish_time is not None,
            'duration': str(player.finish_time - player.start_time) if player.finish_time else None,
            'completed_questions': player.completed_questions.count(),
            'total_questions': total_questions,
            'hints_used': player.total_hints_used,
            'correct_attempts': player.correct_attempts,
            'total_attempts': player.total_attempts,
            'accuracy': round((player.correct_attempts / player.total_attempts * 100) if player.total_attempts > 0 else 0)
        } for player in players[:10]]
    
    async def send_leaderboard(self):
        leaderboard_data = await self.get_leaderboard_data()
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'leaderboard': leaderboard_data
        }))