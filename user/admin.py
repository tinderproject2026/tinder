from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'birth_date', 'gender', 'city']
    search_fields = ['username', 'name']
