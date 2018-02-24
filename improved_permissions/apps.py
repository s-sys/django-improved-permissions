""" permissions configs """
import inspect
from importlib import import_module

from django.apps import AppConfig
from django.conf import settings

from improved_permissions.roles import RoleManager
from improved_permissions.utils import is_role


class ImprovedPermissionsConfig(AppConfig):
    name = 'improved_permissions'
    verbose_name = 'Django Improved Permissions'

    def ready(self):
        """
        Find for Role class implementations
        on all apps in order to auto-register.
        """
        if RoleManager.get_roles():
            return

        for app_name in settings.INSTALLED_APPS:
            try:
                mod = import_module('{app}.roles'.format(app=app_name))
                rc_list = [obj[1] for obj in inspect.getmembers(mod, is_role)]
                for roleclass in rc_list:
                    RoleManager.register_role(roleclass)
            except ImportError:
                pass
