from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from decouple import config

class Command(BaseCommand):
    help = "Create a superuser if it doesn't exist"

    def handle(self, *args, **options):
        phone_number = config("ADMIN_USER")
        password = config("ADMIN_PASSWORD")
        user = CustomUser.objects.filter(phone_number=phone_number).first()

        if user:
            self.stdout.write(self.style.SUCCESS("Admin already exists."))
        else:
            CustomUser.objects.create_superuser(
                phone_number=phone_number,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("Successfully created admin user."))
