from django.apps import AppConfig
import os

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        if os.environ.get("AUTO_CREATE_ADMIN") == "True":
            from django.contrib.auth import get_user_model
            User = get_user_model()

            username = os.environ.get("ADMIN_USERNAME", "admin")
            email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
            password = os.environ.get("ADMIN_PASSWORD", "admin123")

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
