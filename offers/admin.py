from django.contrib import admin
from .models import Offer, OfferUsage


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'discount_amount', 'start_date', 'end_date', 'is_active', 'offer_status', 'usage_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'code')
    readonly_fields = ('code', 'usage_count', 'offer_status')
    fieldsets = (
        ('Offer Details', {
            'fields': ('name', 'code', 'discount_amount', 'image', 'start_date', 'end_date', 'is_active')
        }),

    )

    def offer_status(self, obj):
        return obj.offer_status()

    offer_status.short_description = 'Status'

    def usage_count(self, obj):
        return obj.usage_count()

    usage_count.short_description = 'Usage Count'


@admin.register(OfferUsage)
class OfferUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'offer', 'phone_identifier', 'email_identifier', 'used_at')
    list_filter = ('used_at', 'offer')
    search_fields = ('offer__code', 'phone_identifier', 'email_identifier')
    readonly_fields = ('used_at',)
