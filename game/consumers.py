import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PlayerProgress

class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("leaderboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("leaderboard", self.channel_name)

    async def receive(self, text_data):
        pass  # We don't expect to receive messages from clients

    async def leaderboard_update(self, event):
        # Send leaderboard update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'leaderboard_update',
            'leaderboard': event['leaderboard']
        }))

    @database_sync_to_async
    def get_leaderboard_data(self):
        players = PlayerProgress.objects.select_related('user').order_by('-score')
        return [
            {
                'username': player.user.username,
                'score': player.score,
                'rank': idx + 1,
                'completed': player.is_game_completed()
            }
            for idx, player in enumerate(players)
        ] 