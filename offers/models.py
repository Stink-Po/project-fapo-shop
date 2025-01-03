from django.db import models
from django.contrib.auth import get_user_model
import string
import random
from django.utils.timezone import now

User = get_user_model()


class Offer(models.Model):
    name = models.CharField(max_length=255)  # Name of the event (e.g., Black Friday)
    code = models.CharField(max_length=15, unique=True, blank=True)  # Allow blank initially
    discount_amount = models.PositiveIntegerField()  # Discount value
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    start_date = models.DateTimeField()  # When the offer becomes active
    end_date = models.DateTimeField()  # When the offer expires
    is_active = models.BooleanField(default=True)  # To manually enable/disable the offer

    def __str__(self):
        return f"{self.name} ({self.code})"

    def generate_unique_code(self):
        length = 8
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not Offer.objects.filter(code=code).exists():
                return code

    def check_offer(self):
        if self.is_active:
            today = now()
            if self.start_date <= today <= self.end_date:
                return True
            return False

    def offer_status(self):
        if self.start_date > now():
            return "پیش رو"
        if self.start_date <= now() < self.end_date:
            return "فعال"
        return "منقضی شده"

    def usage_count(self):
        return self.offerusage_set.count()

    @staticmethod
    def get_future_offers():
        """
        Returns all offers that will be active in the future.
        """
        return Offer.objects.filter(
            start_date__gt=now(),
            is_active=True,
            image__isnull=False
        ).exclude(image="")

    @staticmethod
    def get_active_offers():
        """
        Returns all currently active offers.
        """
        return Offer.objects.filter(
            start_date__lte=now(),
            end_date__gte=now(),
            is_active=True,
            image__isnull=False
        ).exclude(image="")

    @staticmethod
    def get_outdated_offers():
        """
        Returns all offers that have expired.
        """
        return Offer.objects.filter(
            end_date__lt=now(),
            image__isnull=False
        ).exclude(image="")

    def save(self, *args, **kwargs):
        if not self.code:  # Ensure the code is set only if blank
            self.code = self.generate_unique_code()
        super(Offer, self).save(*args, **kwargs)


class OfferUsage(models.Model):
    phone_identifier = models.CharField(max_length=255, null=True, blank=True)
    email_identifier = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who used the offer
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)  # The offer code
    used_at = models.DateTimeField(auto_now_add=True)  # Timestamp of usage

    class Meta:
        unique_together = ('user', 'offer')
