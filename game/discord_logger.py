import os
import aiohttp
from datetime import datetime
from .discord_config import DiscordChannels, DiscordColors, DiscordEmbedTitles
import logging

class DiscordLogger:
    def __init__(self):
        self.webhook_urls = {
            DiscordChannels.CLUE_LOGS.value: os.getenv('DISCORD_CLUE_WEBHOOK'),
            DiscordChannels.HINT_LOGS.value: os.getenv('DISCORD_HINT_WEBHOOK'),
            DiscordChannels.USER_ACTIVITY.value: os.getenv('DISCORD_USER_WEBHOOK'),
            DiscordChannels.ACHIEVEMENT_LOGS.value: os.getenv('DISCORD_ACHIEVEMENT_WEBHOOK'),
            DiscordChannels.WRONG_ANSWER_LOGS.value: os.getenv('DISCORD_WRONG_ANSWER_WEBHOOK'),
            DiscordChannels.COMPLETION_LOGS.value: os.getenv('DISCORD_COMPLETION_WEBHOOK')
        }

    async def _send_webhook(self, channel: str, embed: dict) -> bool:
        webhook_url = self.webhook_urls.get(channel)
        if not webhook_url:
            logging.error(f"No webhook URL found for channel: {channel}")
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json={'embeds': [embed]}) as response:
                    if response.status != 204:
                        logging.error(f"Discord webhook failed with status {response.status}")
                        response_text = await response.text()
                        logging.error(f"Response: {response_text}")
                    return response.status == 204
        except Exception as e:
            logging.error(f"Error sending Discord webhook: {str(e)}")
            return False

    def _create_base_embed(self, title: str, color: int) -> dict:
        return {
            'title': title.value if hasattr(title, 'value') else str(title),  # Handle both enum and string
            'color': color.value if hasattr(color, 'value') else color,  # Handle both enum and string
            'timestamp': datetime.utcnow().isoformat()
        }

    async def log_clue_solved(self, username: str, clue_number: int, time_taken: float) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.CLUE_SOLVED,
            DiscordColors.CLUE_SOLVED
        )
        embed['description'] = f'**Player:** {username}\n**Clue:** #{clue_number}\n**Time Taken:** {time_taken:.2f}s'
        return await self._send_webhook(DiscordChannels.CLUE_LOGS.value, embed)

    async def log_hint_used(self, username: str, clue_number: int, hint_number: int) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.HINT_USED,
            DiscordColors.HINT_USED
        )
        embed['description'] = f'**Player:** {username}\n**Clue:** #{clue_number}\n**Hint:** #{hint_number}'
        return await self._send_webhook(DiscordChannels.HINT_LOGS.value, embed)

    async def log_user_activity(self, username: str, action: str) -> bool:
        title = {
            'register': DiscordEmbedTitles.USER_REGISTER,
            'login': DiscordEmbedTitles.USER_LOGIN,
            'logout': DiscordEmbedTitles.USER_LOGOUT
        }.get(action.lower())

        if not title:
            return False

        embed = self._create_base_embed(title, DiscordColors.USER_ACTIVITY)
        embed['description'] = f'**Player:** {username}'
        return await self._send_webhook(DiscordChannels.USER_ACTIVITY.value, embed)

    async def log_achievement(self, username: str, achievement_name: str, description: str) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.ACHIEVEMENT,
            DiscordColors.ACHIEVEMENT
        )
        embed['description'] = f'**Player:** {username}\n**Achievement:** {achievement_name}\n**Description:** {description}'
        return await self._send_webhook(DiscordChannels.ACHIEVEMENT_LOGS.value, embed)

    async def log_wrong_answer(self, username: str, clue_number: int, attempt: str) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.WRONG_ANSWER,
            DiscordColors.WRONG_ANSWER
        )
        embed['description'] = f'**Player:** {username}\n**Clue:** #{clue_number}\n**Attempt:** {attempt}'
        return await self._send_webhook(DiscordChannels.WRONG_ANSWER_LOGS.value, embed)

    async def log_hunt_completion(self, username: str, total_time: float, hints_used: int) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.COMPLETION,
            DiscordColors.COMPLETION
        )
        embed['description'] = f'**Player:** {username}\n**Total Time:** {total_time:.2f}s\n**Hints Used:** {hints_used}'
        return await self._send_webhook(DiscordChannels.COMPLETION_LOGS.value, embed)

    async def log_game_progress(self, username: str, question_number: int, current_score: int) -> bool:
        embed = self._create_base_embed(
            DiscordEmbedTitles.CLUE_SOLVED,
            DiscordColors.CLUE_SOLVED
        )
        embed['description'] = f'**Player:** {username}\n**Current Question:** #{question_number}\n**Current Score:** {current_score}'
        return await self._send_webhook(DiscordChannels.CLUE_LOGS.value, embed)

    async def log_high_score(self, username: str, score: int) -> bool:
        embed = self._create_base_embed(
            "🏅 New High Score",
            DiscordColors.CLUE_SOLVED.value
        )
        embed['description'] = f'**Player:** {username}\n**New High Score:** {score}'
        return await self._send_webhook(DiscordChannels.CLUE_LOGS.value, embed)


# Create a singleton instance
discord_logger = DiscordLogger()