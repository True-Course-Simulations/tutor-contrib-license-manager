from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    """
    Create or update a license-manager superadmin user.

    Usage examples (inside the license-manager container via Tutor):

        # Non-interactive, SSO-only superadmin (no password)
        ./manage.py create_license_manager_superadmin \
            --username dev \
            --email dev@example.com \
            --no-password

        # Non-interactive, with password (local admin login allowed)
        ./manage.py create_license_manager_superadmin \
            --username licadmin \
            --email licadmin@example.com \
            --password 'SomeStrongPassword123'

        # Interactive (will prompt)
        ./manage.py create_license_manager_superadmin
    """

    help = "Create or update a superadmin user for License Manager."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            help="Username for the superadmin account.",
        )
        parser.add_argument(
            "--email",
            dest="email",
            help="Email for the superadmin account.",
        )
        parser.add_argument(
            "--password",
            dest="password",
            help="Password for the superadmin account (optional if using --no-password).",
        )
        parser.add_argument(
            "--no-password",
            action="store_true",
            dest="no_password",
            help="Create the superadmin without setting a usable password "
                 "(SSO-only login).",
        )

    def handle(self, *args, **options):
        username = options.get("username")
        email = options.get("email")
        password = options.get("password")
        no_password = options.get("no_password")

        # Basic interactive prompts if values are missing
        if not username:
            username = input("Username: ").strip()
        if not email:
            email = input("Email: ").strip()

        if not username:
            raise CommandError("Username is required.")
        if not email:
            raise CommandError("Email is required.")

        if password and no_password:
            raise CommandError("You cannot specify both --password and --no-password.")

        # If neither provided, ask if we should set a password
        if not password and not no_password:
            use_password = input(
                "Set a local password for this user? [y/N]: "
            ).strip().lower()
            if use_password == "y":
                password = input("Password (will be stored as a hash): ").strip()
            else:
                no_password = True

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        # If existing user had a different email, update it.
        if user.email != email:
            user.email = email

        user.is_staff = True
        user.is_superuser = True

        if password:
            user.set_password(password)
        elif no_password:
            # SSO-only account: ensures no local password login
            user.set_unusable_password()

        user.save()

        if created:
            msg = f"Created new superadmin user '{username}'."
        else:
            msg = f"Updated existing user '{username}' to be a superadmin."

        if password:
            msg += " Local admin password has been set."
        else:
            msg += " No local password has been set (SSO-only login)."

        self.stdout.write(self.style.SUCCESS(msg))
