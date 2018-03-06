""" permissions configs """
from django.apps import AppConfig

from improved_permissions.utils import autodiscover, register_cleanup


class ImprovedPermissionsConfig(AppConfig):
    name = 'improved_permissions'
    verbose_name = 'Django Improved Permissions'

    def ready(self):
        register_cleanup()
        autodiscover()
