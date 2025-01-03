from django.urls import path
from .views import load_cities

app_name = 'cities'

urlpatterns = [
    path("ajax/load-cities/", load_cities, name="load_cities"),
    ]