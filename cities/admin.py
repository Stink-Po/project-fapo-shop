from django.contrib import admin
from .models import State, City


# Define the admin interface for the State model
class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the 'name' field in the admin list view
    search_fields = ('name',)  # Allow searching by the 'name' field


# Define the admin interface for the City model
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')  # Display 'name' and 'state' fields in the admin list view
    list_filter = ('state',)  # Add a filter for 'state' in the right sidebar
    search_fields = ('name', 'state__name')  # Allow searching by city name and state name


# Register the models with the custom admin classes
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
