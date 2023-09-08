from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ('email', 'is_staff')
    list_filter = ()
    search_fields = ('email', 'first_name', 'last_name')

    list_display = (
        'email', 'first_name', 'last_name', 'referred_users_count',
        'open_rate', 'has_sunday_mails_prize', 'is_active', 'recency'
    )

    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name', 'dispatch_time')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name'),
        }),
    )

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder']):
            return super(UserAdmin, self).get_model_perms(request)
        else:
            return {}


admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
