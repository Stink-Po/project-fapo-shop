from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class Tickets(models.Model):
    class TicketStatus(models.TextChoices):
        PENDING = 'pending', 'در انتظار پاسخ'
        APPROVED = 'approved', 'پاسخ داده شده'
        CLOSED = 'closed', 'بسته شده'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(choices=TicketStatus.choices, default=TicketStatus.PENDING, max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tickets:ticket_details", args=[
            self.id,
        ])


class TicketResponse(models.Model):
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name='response')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

