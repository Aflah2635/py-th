# 🌐 CyberQuest: Digital Treasure Hunt

A cyberpunk-themed treasure hunt game built with Django, featuring real-time updates, neon aesthetics, and immersive gameplay.

## ⚡ Features

- 🎮 Cyberpunk UI/UX with neon glow effects
- 📊 Real-time leaderboard with WebSocket updates
- 🔐 Secure authentication system
- 📱 Fully responsive design
- 🎯 Progressive hint system
- 🔄 Live progress tracking
- 👾 Interactive clue reveals with animations
- 🛠️ Admin dashboard for game management

## 🚀 Tech Stack

- **Backend**: Django 4.2.9, Channels 4.0.0
- **Server**: Daphne 4.1.2, Gunicorn 21.2.0
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Real-time**: WebSocket (Django Channels)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Theme**: Cyberpunk Neon (Dark mode with neon accents)
- **Static Files**: Whitenoise 6.6.0

## 💻 Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/py-th.git
cd py-th
```
2. **Create Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Environment Setup Create a .env file in the root directory:**
```bash
SECRET_KEY=your-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```
5. **Create Admin User**
```bash
python manage.py createsuperuser
```
6. **Run the Server**
```bash
python manage.py runserver
```
## 🌐 Access Points
- Game Interface : http://127.0.0.1:8000/game/
- Admin Panel : http://127.0.0.1:8000/admin/
- Leaderboard : http://127.0.0.1:8000/leaderboard/
## 🎮 Game Features
- Progressive Difficulty : Challenges increase in complexity
- Hint System : Strategic help system with cooldown
- Real-time Updates : Live leaderboard and progress tracking
- Secure Authentication : Protected game progress
- Mobile Optimization : Play on any device
## 🛠️ Development
- Built with Django's latest security features
- WebSocket integration for real-time updates
- Responsive design using Bootstrap 5
- Custom cyberpunk UI components
- Optimized for performance with Whitenoise
## 🔐 Security Notes
- Always use a secure secret key in production
- Keep DEBUG=False in production
- Update ALLOWED_HOSTS for production domains
- Use HTTPS in production
- Regular security updates for dependencies
## 🤝 Contributing
1. Fork the repository
2. Create your feature branch ( git checkout -b feature/AmazingFeature )
3. Commit your changes ( git commit -m 'Add some AmazingFeature' )
4. Push to the branch ( git push origin feature/AmazingFeature )
5. Open a Pull Request
## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
## 🔮 Future Enhancements
- AR integration for location-based clues
- Advanced analytics dashboard
- Social sharing features
- Achievement system
- Multi-language support
