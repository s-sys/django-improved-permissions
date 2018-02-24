""" permissions configs """
from django.apps import AppConfig

from improved_permissions.roles import Role
from improved_permissions.utils import discover_and_register_roles


class ImprovedPermissionsConfig(AppConfig):
    name = 'improved_permissions'
    verbose_name = 'Django Improved Permissions'

    def ready(self):
        if not Role.get_roles():
            discover_and_register_roles()
