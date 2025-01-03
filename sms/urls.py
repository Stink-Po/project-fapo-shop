from django.urls import path
from .views import send_otp

app_name = "sms"

urlpatterns = [
    path("send-otp/", send_otp, name="send_otp"),
]