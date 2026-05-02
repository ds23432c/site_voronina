import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a superuser from Railway environment variables."

    def handle(self, *args, **options):
        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()
        username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()

        if not email or not password:
            self.stdout.write(self.style.WARNING("DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required."))
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(email=email)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=["is_staff", "is_superuser", "is_active", "password"])

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Superuser {action}: {email}"))
        self.stdout.write(self.style.SUCCESS(f"Login: {email}"))
        self.stdout.write(self.style.SUCCESS(f"Password: {password}"))

        if username:
            self.stdout.write(self.style.NOTICE(f"DJANGO_SUPERUSER_USERNAME was provided as '{username}' but email is used as the login."))
