from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [    
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('game/', views.game_interface, name='game_interface'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('get_hint/', views.get_hint, name='get_hint'),
    path('help/', views.help_view, name='help'),
    path('.well-known/appspecific/com.chrome.devtools.json', views.chrome_devtools_stub, name='chrome_devtools'),
    path('test-webhook/', views.test_discord_webhook, name='test-webhook'),
    path('get_hint/', views.get_hint, name='get_hint')
]
path('logout/', views.logout_view, name='logout'),