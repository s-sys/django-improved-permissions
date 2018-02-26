""" permissions configs """
from django.apps import AppConfig

from improved_permissions.utils import autodiscover


class ImprovedPermissionsConfig(AppConfig):
    name = 'improved_permissions'
    verbose_name = 'Django Improved Permissions'

    def ready(self):
        autodiscover()
