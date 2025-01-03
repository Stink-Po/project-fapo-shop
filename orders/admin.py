from django.contrib import admin
from .models import Order, OrderItem, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'status', 'created', 'updated', 'paid', 'get_total_cost', 'track_id'
    )
    list_filter = ('status', 'paid', 'created', 'updated')
    search_fields = ('id', 'track_id', 'email', 'phone')
    readonly_fields = ('created', 'updated', 'get_total_cost')
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'track_id', 'paid')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'phone', 'email', 'address', 'province', 'city', 'postal_code')
        }),
        ('Discount & Shipping', {
            'fields': ('discount_code', 'discount_amount', 'post_follow_up')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )

    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Total Cost'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'color', 'quantity', 'price', 'discount', 'get_cost')
    list_filter = ('order', 'product', 'color')
    search_fields = ('product__name', 'color')
    readonly_fields = ('get_cost',)

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Total Cost'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'order', 'timestamp', 'status', 'amount', 'track_id', 'ref_number', 'result'
    )
    list_filter = ('status', 'timestamp')
    search_fields = ('id', 'track_id', 'ref_number', 'card_number')
    readonly_fields = ('id',)
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'order', 'amount', 'status', 'timestamp', 'card_number')
        }),
        ('Tracking', {
            'fields': ('track_id', 'ref_number')
        }),
        ('Details', {
            'fields': ('description', 'result', 'message')
        }),
    )
