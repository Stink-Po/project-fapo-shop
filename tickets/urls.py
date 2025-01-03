from django.urls import path
from . import views

from . import views

app_name = "tickets"

urlpatterns = [
    path("add-response/<int:ticket_id>/", views.add_comment_to_ticket_profile, name="add_comment_to_ticket_profile"),
    path("close-ticket/<int:ticket_id>/", views.close_ticket_profile, name="close_ticket"),
]
