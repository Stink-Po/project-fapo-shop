from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, ReferralCode, Profile, DiscountCodes, UserIdentifier
from django import forms
from django.utils import timezone
from datetime import timedelta

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'

class DiscountCodesForm(forms.ModelForm):
    class Meta:
        model = DiscountCodes
        fields = '__all__'

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'email', 'is_staff', 'is_superuser', 'is_active', 'score', 'get_referral_code', 'is_new')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone_number', 'password', 'score')}),
        ('Personal Info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_new', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'score'),
        }),
    )
    search_fields = ('phone_number', 'email')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = (ProfileInline,)

    def get_referral_code(self, obj):
        return obj.get_referral_code() or 'No code'

    get_referral_code.short_description = 'Referral Code'


class ReferralCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user')
    search_fields = ('code', 'user__phone_number')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'province', 'city', 'email', 'join_date')
    search_fields = ('user__phone_number', 'first_name', 'last_name', 'city', 'email')


class DiscountCodesAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'amount', 'used', 'expire_date', 'created', 'is_code_valid')
    list_filter = ('used', 'expire_date')
    search_fields = ('user__phone_number', 'code')
    ordering = ('-created',)

    def is_code_valid(self, obj):
        return obj.check_code()

    is_code_valid.short_description = 'Is Valid'
    is_code_valid.boolean = True

    def get_form(self, request, obj=None, **kwargs):
        """
        Override the get_form method to pass in initial values for new discount codes.
        """
        # Get the form instance (fixing previous bug)
        form = super().get_form(request, obj, **kwargs)

        # Set the initial values only if it's a new object (obj is None)
        if obj is None:
            # Set initial values for code and expire_date
            form.base_fields['code'].initial = DiscountCodes().generate_unique_code()  # Ensure this function generates a unique code
            form.base_fields['expire_date'].initial = timezone.now() + timedelta(days=30)  # Set expiry date 30 days from now

        return form

@admin.register(UserIdentifier)
class UserIdentifierAdmin(admin.ModelAdmin):
    list_display = ('id', 'identifier')  # Fields to display in the list view
    search_fields = ('identifier',)     # Enable search by the `identifier` field
    ordering = ('id',)

# Registering the models with their respective admin configurations
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ReferralCode, ReferralCodeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(DiscountCodes, DiscountCodesAdmin)
