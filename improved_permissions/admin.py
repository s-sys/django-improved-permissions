""" permissions admin configs """
from django.contrib import admin

from improved_permissions.models import RolePermission, UserRole

admin.site.register(UserRole)
admin.site.register(RolePermission)
