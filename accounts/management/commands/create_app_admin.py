from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Create the SRMCEM application's custom admin account if it does not already exist."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        username = options["username"].strip()
        email = options["email"].strip()
        password = options["password"]

        if not username or not email or not password:
            raise CommandError("username, email and password are required")

        existing_username = User.objects.filter(username=username).first()
        if existing_username:
            if existing_username.role != User.ROLE_ADMIN:
                raise CommandError(
                    f'Username "{username}" already belongs to a non-admin account.'
                )
            self.stdout.write(
                self.style.WARNING(
                    f'Admin account "{username}" already exists; leaving it unchanged.'
                )
            )
            return

        if User.objects.filter(email=email).exists():
            raise CommandError(f'Email "{email}" is already in use.')

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=User.ROLE_ADMIN,
        )
        self.stdout.write(
            self.style.SUCCESS(f'Created application admin account "{username}".')
        )
