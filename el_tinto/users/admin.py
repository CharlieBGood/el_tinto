from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy
from django.contrib.auth.admin import UserAdmin

from el_tinto.users.admin_actions.add_meta_users import add_meta_users
from el_tinto.users.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    ordering = ('email', 'is_staff')
    list_filter = ()
    search_fields = ('email', 'first_name', 'last_name')
    actions = [add_meta_users]

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

    def changelist_view(self, request, extra_context=None):
        """
        Change list view to allow run action when no user is selected for
        specific actions.
        """
        if 'action' in request.POST and request.POST['action'] == 'add_meta_users':
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()

                for user in User.objects.all():
                    post.update({ACTION_CHECKBOX_NAME: str(user.id)})

                request._set_post(post)

        return super(UserAdmin, self).changelist_view(request, extra_context)

admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
