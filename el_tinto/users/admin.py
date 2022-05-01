from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ('email', 'is_staff')
    list_display = ['email', 'first_name', 'last_name', 'is_staff']
