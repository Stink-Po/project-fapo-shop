from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.get_order_address, name="get_order_address"),
    path("create-order/", views.save_order_with_user_profile_information, name="create_order"),
    path("new-address/", views.get_new_order_address, name="get_new_order_address"),
    path("send-payment/", views.send_request, name="send_request"),
    path("factor/<int:order_id>/<int:track_id>/", views.factor, name="factor"),
    path("callback/", views.call_back, name="callback"),
    path('download-factor/<int:order_id>/<int:track_id>/', views.download_factor, name='download_factor'),
]
