# Python Treasure Hunt Game

A cyberpunk-themed web-based treasure hunt game built with Django, featuring real-time activity tracking, and comprehensive analytics. The game includes an advanced logging system, performance monitoring, and secure user progression tracking with anti-cheating mechanisms.

## Features

- User Authentication System
- Progressive Clue System
- Hint System with Point Penalties
- Admin Analytics Dashboard
- Real-time Leaderboard
- Secure Answer Submission
- User Progress Tracking
- Internal Activity Logging
- Performance Analytics
- ASGI Support for Real-time Features

## Prerequisites

- Python 3.13+
- Redis Server 7.2+ (for caching, channels, and real-time features)
- PostgreSQL 15+ Database
- Node.js 18+ (for frontend development)

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Aflah2635/py-th.git
   ```

2. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in .env file:
   ```bash
   # Django Configuration
   DJANGO_SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=*

5. Set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Features in Detail

### User System
- Secure registration and authentication
- Real-time progress tracking
- Dynamic score management
- User activity history
- Profile customization

### Game Mechanics
- Sequential clue progression system
- Adaptive hint system with configurable penalties
- Secure answer validation
- Real-time progress updates
- Anti-cheating mechanisms

### Admin Features
- Comprehensive analytics dashboard
- Real-time player activity monitoring
- Detailed clue performance statistics
- User progression tracking
- Custom analytics reports
- Activity log viewer

### Logging System
- Comprehensive activity logging
- Performance metrics tracking
- Error tracking and reporting
- User behavior analytics
- Security audit logging

### Technical Features
- ASGI support for real-time features
- Redis caching and pub/sub for improved performance
- PostgreSQL for robust data storage
- Scalable microservices architecture
- Cross-origin resource sharing support
- Discord bot integration for notifications
- Cyberpunk-themed UI with responsive design
- WebSocket-based real-time updates
- Rate limiting and request throttling
- Automated backup and recovery system

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
This project follows PEP 8 style guide for Python code. To check your code style:
```bash
flake8 .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.