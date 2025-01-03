from django.contrib import admin
from .models import Tickets, TicketResponse


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created', 'updated')
    list_filter = ('status', 'created', 'updated')
    search_fields = ('title', 'description')


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'created')
    list_filter = ('created',)
    search_fields = ('response',)