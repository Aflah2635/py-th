# Python Treasure Hunt Game

A web-based treasure hunt game built with Django, featuring real-time Discord integration for activity tracking and analytics.

## Features

- User Authentication System
- Progressive Clue System
- Real-time Discord Logging
- Hint System with Point Penalties
- Admin Analytics Dashboard
- Real-time Leaderboard
- Secure Answer Submission
- User Progress Tracking

## Prerequisites

- Python 3.13+
- Redis Server
- Discord Webhook Integration

## Installation

1. Clone the repository
```bash
git clone https://github.com/Aflah2635/py-th.git
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Fill .env file:
   ```bash
   # Django Settings
DJANGO_SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=*

# Discord Webhooks
DISCORD_CLUE_WEBHOOK=
DISCORD_HINT_WEBHOOK=
DISCORD_USER_WEBHOOK=
DISCORD_WRONG_ANSWER_WEBHOOK=
DISCORD_COMPLETION_WEBHOOK=
   ```
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Features in Detail

### User System
- Registration and authentication
- Progress tracking
- Score management
### Game Mechanics
- Sequential clue progression
- Hint system with score penalties
- Answer validation
- Real-time progress updates
### Admin Features
- Analytics dashboard
- Player activity monitoring
- Clue performance statistics
- User progression tracking
### Discord Integration
- Real-time activity logging
- Clue completion tracking
- Hint usage monitoring
- Game completion notifications