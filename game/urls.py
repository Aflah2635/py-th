from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_home, name='game_home'),
    path('register/', views.register, name='register'),
    path('submit/', views.submit_answer, name='submit_answer'),
    path('hint/<int:question_id>/', views.get_hint, name='get_hint'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]