from django.urls import path
from . import views

app_name = "offers"

urlpatterns = [
    path("", views.offer_list, name="offer_list"),
    path("جشنواره/<int:offer_id>", views.offer_detail, name="offer_detail"),
]