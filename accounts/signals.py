from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import ReferralCode, UserIdentifier



@receiver(user_logged_in)
def handle_referral_on_login(sender, request, user, **kwargs):
    # Check if the user is logging in for the first time
    unique_identifier = user.phone_number if user.phone_number else user.email
    print(f"this is inside signals {unique_identifier}")
    user_exists_before = UserIdentifier.objects.filter(identifier=unique_identifier).exists()
    if not user_exists_before:
        if user.is_new:
            referral_code = request.session.get("referral_code")
            if referral_code:
                try:
                    # Attempt to get the referral code from the database
                    refer_user = ReferralCode.objects.get(code=referral_code)
                    refer_user.invites += 1
                    refer_user.user.add_score(score=5)  # Assuming add_score adds points to the referred user
                    refer_user.save()
                except ReferralCode.DoesNotExist:
                    pass

        # Set the user's new status to False after handling the referral


