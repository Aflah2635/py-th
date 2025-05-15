from enum import Enum

class DiscordChannels(Enum):
    CLUE_LOGS = "clue_logs"
    HINT_LOGS = "hint_logs"
    USER_ACTIVITY = "user_activity"
    ACHIEVEMENT_LOGS = "achievement_logs"
    WRONG_ANSWER_LOGS = "wrong_answer_logs"
    COMPLETION_LOGS = "completion_logs"

class DiscordColors(Enum):
    CLUE_SOLVED = 0x00FF00  # Green
    HINT_USED = 0xFFA500    # Orange
    USER_ACTIVITY = 0x0000FF # Blue
    ACHIEVEMENT = 0xFFD700   # Gold
    WRONG_ANSWER = 0xFF0000  # Red
    COMPLETION = 0x9400D3    # Purple

class DiscordEmbedTitles(Enum):
    CLUE_SOLVED = "🎯 Clue Solved"
    HINT_USED = "💡 Hint Used"
    USER_REGISTER = "👋 New User Registration"
    USER_LOGIN = "✅ User Login"
    USER_LOGOUT = "👋 User Logout"
    ACHIEVEMENT = "🏆 Achievement Unlocked"
    WRONG_ANSWER = "❌ Wrong Answer"
    COMPLETION = "🎉 Hunt Completed"