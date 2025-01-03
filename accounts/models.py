from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta
import string
import random
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        email = extra_fields.get('email')

        if email:
            try:
                existing_user = CustomUser.objects.get(email=email)
                return existing_user
            except CustomUser.DoesNotExist:
                pass

        if not phone_number:
            raise ValueError('The Phone Number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    score = models.PositiveIntegerField(default=10, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        is_new_user = self.pk is None
        super().save(*args, **kwargs)
        self.refresh_from_db()
        if is_new_user:
            self.generate_referral_code()
            this_user = CustomUser.objects.get(pk=self.pk)
            try:
                int(this_user.phone_number)
                if str(this_user.phone_number) in str(this_user.email):
                    identifier = this_user.email
                else:
                    identifier = this_user.phone_number
            except ValueError:
                identifier = this_user.email
            print(identifier)
            if not UserIdentifier.objects.filter(identifier=identifier).exists():
                DiscountCodes.objects.create(user=self)
            Profile.objects.get_or_create(user=self)

    def add_score(self, score):
        self.score += score
        self.save()

    def decrease_score(self, score):
        self.score -= score
        self.save()

    def generate_referral_code(self):
        code_length = 19
        characters = string.ascii_letters + string.digits
        unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        while ReferralCode.objects.filter(code=unique_code).exists():
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        ReferralCode.objects.create(user=self, code=unique_code)

    def get_referral_code(self):
        try:
            return self.referralcode.code
        except ReferralCode.DoesNotExist:
            return None

    def __str__(self):
        return self.phone_number if self.phone_number else self.email


class ReferralCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    invites = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.code


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    zip_code = models.CharField(max_length=11, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    join_date = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"profile of {self.user.phone_number}"


def generate_unique_code():
    length = 14
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if not DiscountCodes.objects.filter(code=code).exists():
            return code


class DiscountCodes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='discount_codes')
    amount = models.PositiveIntegerField(default=10)
    code = models.CharField(max_length=10, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    expire_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:  # Ensure the code is blank for new instances
            self.code = self.generate_unique_code()
        if not self.expire_date:
            self.expire_date = timezone.now() + timedelta(days=30)
        super(DiscountCodes, self).save(*args, **kwargs)

    def generate_unique_code(self):
        length = 10
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not DiscountCodes.objects.filter(code=code).exists():
                return code

    def check_code(self):
        if self.expire_date > timezone.now() and not self.used:
            return True
        return False



class UserIdentifier(models.Model):
    identifier = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.identifier
