""" permissions admin configs """
from django.contrib import admin

from improved_permissions.models import RolePermission

admin.site.register(RolePermission)
