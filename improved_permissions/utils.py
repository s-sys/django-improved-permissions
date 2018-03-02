""" permissions utils """
import inspect

from improved_permissions.exceptions import (ImproperlyConfigured,
                                             ParentNotFound, RoleNotFound)


def is_role(role_class):
    """
    Check if the argument is a valid Role class.
    This method DOES NOT check if the class is registered in RoleManager.
    """
    from improved_permissions.roles import Role
    return inspect.isclass(role_class) and issubclass(role_class, Role) and role_class != Role


def autodiscover():
    """
    Find for Role class implementations
    on all apps in order to auto-register.
    """
    from importlib import import_module
    from django.conf import settings
    from improved_permissions.roles import RoleManager

    try:
        # Check if the Permission model
        # is ready to be used.
        from django.contrib.auth.models import Permission
        from django.db.utils import OperationalError
        Permission.objects.count()
    except OperationalError:  # pragma: no cover
        return

    # If any role was registered already,
    # do not perform the autodiscover.
    if RoleManager.get_roles():  # pragma: no cover
        return

    # Looking for Role classes in "roles.py".
    for app_name in settings.INSTALLED_APPS:
        try:
            mod = import_module('{app}.roles'.format(app=app_name))
            rc_list = [obj[1] for obj in inspect.getmembers(mod, is_role)]
            for roleclass in rc_list:
                RoleManager.register_role(roleclass)
        except ImportError:
            pass


def get_roleclass(role_class):
    """
    Get the role class signature
    by string or by itself.
    """
    from improved_permissions.roles import RoleManager
    roles_list = RoleManager.get_roles()
    if role_class in roles_list:
        # Already a Role class.
        return role_class

    elif isinstance(role_class, str):
        # Trying to get via string.
        for role in roles_list:
            if role.get_class_name() == role_class:
                return role

    raise RoleNotFound()


def get_model(model):
    """
    Transforms a string representation
    into a valid Django Model class.
    """
    from django.apps import apps
    from django.db.models import Model

    result = None
    if inspect.isclass(model) and issubclass(model, Model):
        result = model
    elif isinstance(model, str):
        app_label, modelname = model.split('.')
        try:
            result = apps.get_model(app_label, modelname)
        except LookupError:
            pass
    return result


def string_to_permission(perm):
    """
    Transforms a string representation
    into a Permission instance.
    """
    from django.contrib.auth.models import Permission
    try:
        app_label, codename = perm.split('.')
    except (ValueError, IndexError):  # pragma: no cover
        raise AttributeError
    return Permission.objects.get(content_type__app_label=app_label, codename=codename)


def permission_to_string(perm):
    """
    Transforms a Permission instance
    into a string representation.
    """
    app_label = perm.content_type.app_label
    codename = perm.codename
    return '%s.%s' % (app_label, codename)


def get_permissions_list(models_list):
    """
    Given a list of Model instances or a Model
    classes, return all Permissions related to it.
    """
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    ct_list = ContentType.objects.get_for_models(*models_list)
    ct_ids = [ct.id for cls, ct in ct_list.items()]

    return list(Permission.objects.filter(content_type_id__in=ct_ids))


def get_parents(model):
    """
    Return the list of instances refered
    as "parents" of a given model instance.
    """
    result = list()
    if hasattr(model, 'RoleOptions'):
        options = getattr(model, 'RoleOptions')
        if hasattr(options, 'permission_parents'):
            parents_list = getattr(options, 'permission_parents')
            for parent in parents_list:
                if hasattr(model, parent):
                    result.append(getattr(model, parent))
                else:
                    raise ParentNotFound('The field "%s" was not found in the '
                                         'model "%s".' % (parent, str(model)))
    return result


def is_unique_together(model):
    """
    Return True if the model does not
    accept multiple roles attached to
    it using the user instance.
    """
    if hasattr(model, 'RoleOptions'):
        options = getattr(model, 'RoleOptions')
        if hasattr(options, 'unique_together'):
            ut_value = getattr(options, 'unique_together')
            if isinstance(ut_value, bool):
                return ut_value
            raise ImproperlyConfigured('The field "unique_together" of "%s" must '
                                       'be a bool value.' % (str(model)))
    return False


def inherit_check(role_obj, permission):
    """
    Check if the role class has the following
    permission in inherit mode.
    """
    from improved_permissions.roles import ALLOW_MODE

    role = get_roleclass(role_obj.role_class)
    if role.inherit is True:
        if role.get_inherit_mode() == ALLOW_MODE:
            return True if permission in role.inherit_allow else False
        return False if permission in role.inherit_deny else True
    return False


def cleanup_handler(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    This function is attached to the post_delete
    signal of all models of Django. Used to remove
    useless role instances and permissions.
    """
    from django.contrib.contenttypes.models import ContentType
    from improved_permissions.models import UserRole
    ct_obj = ContentType.objects.get_for_model(instance)
    UserRole.objects.filter(content_type=ct_obj.id, object_id=instance.id).delete()


def register_cleanup():
    """
    Register the function "cleanup_handler"
    to all models in the project.
    """
    from django.apps import apps
    from django.db.models.signals import post_delete
    from improved_permissions.models import UserRole, RolePermission

    ignore = [UserRole, RolePermission]
    for model in apps.get_models():
        if model not in ignore and hasattr(model, 'id'):
            post_delete.connect(cleanup_handler, sender=model)
