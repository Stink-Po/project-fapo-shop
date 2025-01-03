from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from .models import Profile,UserIdentifier
import re

User = get_user_model()

def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        email = response.get('email')
        first_name = response.get('given_name')
        last_name = response.get('family_name')
        unique_identifier =  email
        user_exists_before = UserIdentifier.objects.filter(identifier=unique_identifier).exists()
        if not user_exists_before:
            UserIdentifier.objects.create(identifier=unique_identifier)
        # Update user fields
        if email:
            user.email = email

        if user.phone_number and not re.match(r'^\d{11}$', user.phone_number):
            user.phone_number = None

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Update or create profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.first_name = first_name
        profile.last_name = last_name
        profile.email = email
        profile.save()

        # Handle login and redirection
        request = kwargs.get('request')  # Get the request object from kwargs
        if request:
            user.backend = 'social_core.backends.google.GoogleOAuth2'
            login(request, user)  # Log the user in regardless of whether they're new

        if user.is_new and not user_exists_before:
            user.is_new = False  # Mark the user as no longer new
            user.save()
            return redirect("accounts:welcome")

        elif user.is_new and user_exists_before:
            user.is_new = False
            user.save()

        # Redirect for existing users
        return redirect("pages:index")

