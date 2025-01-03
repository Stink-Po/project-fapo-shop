from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.index_page, name="index"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("سوالات-متداول/", views.frequency_asked_questions, name="frequency_asked_questions"),
    path("تماس-با-ما/", views.contact, name="contact"),
    path("قوانین-و-مقررات/", views.terms, name="terms"),
    path("درباره-ما/", views.about_us, name="about_us"),
    path("robots.txt", views.robots, name="robots_txt"),
]