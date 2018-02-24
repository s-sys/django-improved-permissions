""" permissions utils """
import inspect
from importlib import import_module

from django.conf import settings

from improved_permissions import exceptions
from improved_permissions.roles import Role


def is_role(cls):
    """
    Check if the argument is a class
    inherited of Role class.
    """
    return inspect.isclass(cls) and issubclass(cls, Role) and cls != Role


def get_roleclass(role_class):
    """
    Get the role class signature
    by string or by itself.
    """
    if issubclass(role_class, Role):
        # Already a Role class.
        return role_class

    elif isinstance(role_class, str):
        # Trying to get via string.
        for role in Role.get_roles():
            if role.get_class_name() == role_class:
                return role

    raise exceptions.RoleNotFound()


def discover_and_register_roles():
    """
    Discover and register all Role
    classes amount the project.
    """
    for app_name in settings.INSTALLED_APPS:
        try:
            mod = import_module('{}.roles'.format(app_name))
            Role._ROLE_CLASSES_LIST += [obj[1] for obj in inspect.getmembers(mod, is_role)]
        except ImportError:
            pass
