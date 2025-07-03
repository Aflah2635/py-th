from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out


class GameConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'

    def ready(self):
        from .activity_log import log_activity
        from django.contrib.auth.models import User

        def on_user_login(sender, request, user, **kwargs):
            log_activity(user, 'login')

        def on_user_logout(sender, request, user, **kwargs):
            log_activity(user, 'logout')

        def on_user_register(sender, instance, created, **kwargs):
            if created:
                log_activity(instance, 'register')

        user_logged_in.connect(on_user_login)
        user_logged_out.connect(on_user_logout)
        post_save.connect(on_user_register, sender=User)
