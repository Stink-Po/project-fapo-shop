from django.urls import path
from . import views


app_name = "staff_area"

urlpatterns = [
    path("", views.main_admin_view, name="main"),
    path("get-data/", views.get_new_data, name="get_data"),
    path("orders-list/", views.main_orders_admin_view, name="orders_list"),
    path("tickets-list/", views.main_tickets_admin_view, name="tickets_list"),
    path("offers/", views.main_offers_admin_view,name="offers"),
    path("ticket-details/<int:ticket_id>/", views.ticket_details_admin_view,name="ticket_details"),
    path("order-details/<int:order_id>/", views.order_details_admin_view,name="order_details"),
    path("print-address/<int:order_id>/", views.print_address, name="print_address"),
]