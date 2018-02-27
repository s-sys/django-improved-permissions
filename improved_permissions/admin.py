""" permissions admin configs """
from django.contrib import admin
from django.contrib.auth.models import Permission

from improved_permissions.models import RolePermission, UserRole

admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
