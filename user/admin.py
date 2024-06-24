# user/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext, gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'role')}),  # Added 'role' here
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),  # Added 'role' here
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')  # Added 'role' here
    search_fields = ('email', 'first_name', 'last_name', 'role')  # Optionally searchable by 'role'
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)  # Optionally unregister the Group model from admin if not needed
