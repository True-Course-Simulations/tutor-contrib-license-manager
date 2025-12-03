from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    """
    Promote an existing License Manager user to superadmin.

    Typical flow:
        1. User logs in once via SSO (creates the user record in License Manager).
        2. Run this command to grant that user superadmin rights.

    Usage:
        ./manage.py promote_license_manager_superadmin --username dev
        ./manage.py promote_license_manager_superadmin --username dev --email dev@example.com
    """

    help = "Promote an existing user to License Manager superadmin (is_staff + is_superuser)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Username of the user to promote.",
        )
        parser.add_argument(
            "--email",
            help="(Optional) Email of the user to promote, for extra safety.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options.get("email")

        qs = User.objects.filter(username=username)
        if email:
            qs = qs.filter(email=email)

        user = qs.first()
        if not user:
            if email:
                raise CommandError(
                    f"No user found with username='{username}' and email='{email}'."
                )
            raise CommandError(f"No user found with username='{username}'.")

        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"User '{user.username}' promoted to License Manager superadmin."
            )
        )
