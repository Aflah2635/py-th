import json
import aiohttp
from typing import Dict, Optional
import os
from datetime import datetime
from discord import Embed, Color

class DiscordLogger:
    def __init__(self):
        from django.conf import settings
        # Initialize webhook URLs for different event types
        webhook_url = settings.DISCORD_WEBHOOK_URL
        self.webhooks: Dict[str, str] = {
            'clue': os.getenv('DISCORD_CLUE_WEBHOOK'),  # Webhook URL for clue events
            'hint': os.getenv('DISCORD_HINT_WEBHOOK'),  # Webhook URL for hint events
            'user_activity': os.getenv('DISCORD_USER_WEBHOOK'),  # Webhook URL for user activity
            'achievement': os.getenv('DISCORD_ACHIEVEMENT_WEBHOOK'),  # Webhook URL for achievements
            'wrong_answer': os.getenv('log_wrong_answer'),  # Webhook URL for wrong answers
            'completion': os.getenv('log_completion')  # Webhook URL for completion events
        }
        
    def set_webhook(self, event_type: str, webhook_url: str) -> None:
        """Set webhook URL for a specific event type."""
        if event_type in self.webhooks:
            self.webhooks[event_type] = webhook_url

    async def send_embed(self, event_type: str, embed: Embed, username: Optional[str] = None) -> bool:
        """Send an embed message to Discord webhook."""
        if not self.webhooks.get(event_type):
            return False

        webhook_url = self.webhooks[event_type]
        payload = {
            'embeds': [embed.to_dict()],
            'username': username or 'Game Logger'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 204
        except Exception:
            return False

    async def log_clue(self, player: str, clue: str) -> bool:
        """Log when a player receives a clue."""
        embed = Embed(
            title="🔍 New Clue Received",
            color=Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Clue", value=clue, inline=True)
        return await self.send_embed('clue', embed, username='Clue Logger')

    async def log_clue_solved(self, player: str, clue: str, time_taken: str) -> bool:
        """Log when a player solves a clue."""
        embed = Embed(
            title="🧩 Clue Solved!",
            color=Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Clue", value=clue, inline=True)
        embed.add_field(name="Time Taken", value=time_taken, inline=True)
        return await self.send_embed('clue', embed, username='Clue Logger')

    async def log_hint_used(self, player: str, clue: str, hint_number: int, points_deducted: int = 0) -> bool:
        """Log when a player receives a hint."""
        embed = Embed(
            title="💡 Hint Used",
            color=Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Clue", value=clue, inline=True)
        embed.add_field(name="Hint Number", value=str(hint_number), inline=True)
        if points_deducted > 0:
            embed.add_field(name="Points Deducted", value=str(points_deducted), inline=True)
        return await self.send_embed('hint', embed, username='Hint Logger')

    async def log_user_activity(self, player: str, activity: str) -> bool:
        """Log player activity."""
        activity_icons = {
            'register': '✅',
            'login': '🚪',
            'logout': '🔒'
        }
        icon = activity_icons.get(activity.lower(), '👤')
        embed = Embed(
            title=f"{icon} User Activity",
            color=Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Action", value=activity, inline=True)
        return await self.send_embed('user_activity', embed, username='Activity Logger')

    async def log_achievement(self, player: str, achievement: str) -> bool:
        """Log player achievements."""
        embed = Embed(
            title="🏆 Achievement Unlocked!",
            color=Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Achievement", value=achievement, inline=True)
        return await self.send_embed('achievement', embed, username='Achievement Logger')

    async def log_wrong_answer(self, player: str, clue: str, attempt: str, attempt_count: int) -> bool:
        """Log wrong answers."""
        if attempt_count < 5:
            return True
        embed = Embed(
            title="🧪 Wrong Answer Submitted",
            color=Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Clue", value=clue, inline=True)
        embed.add_field(name="Attempt", value=attempt, inline=True)
        embed.add_field(name="Attempt Count", value=str(attempt_count), inline=True)
        return await self.send_embed('wrong_answer', embed, username='Answer Logger')

    async def log_completion(self, player: str, rank: int, total_score: int, time_taken: str) -> bool:
        """Log challenge completion."""
        embed = Embed(
            title="🏁 Hunt Completed!",
            color=Color.from_rgb(205, 127, 50),  # Bronze color
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Player", value=player, inline=True)
        embed.add_field(name="Final Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="Total Score", value=str(total_score), inline=True)
        embed.add_field(name="Total Time", value=time_taken, inline=True)
        return await self.send_embed('completion', embed, username='Completion Logger')


# Create a singleton instance
discord_logger = DiscordLogger()