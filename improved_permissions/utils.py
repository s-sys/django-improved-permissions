""" permissions utils """
# pylint: disable=too-many-lines
import inspect

from improved_permissions.exceptions import (ImproperlyConfigured, NotAllowed,
                                             ParentNotFound, RoleNotFound)


def is_role(role_class):
    """
    Check if the argument is a valid Role class.
    This method DOES NOT check if the class is registered in RoleManager.
    """
    from improved_permissions.roles import Role
    return inspect.isclass(role_class) and issubclass(role_class, Role) and role_class != Role


def get_config(key, default):
    """
    Get the dictionary "IMPROVED_PERMISSIONS_SETTINGS"
    from the settings module.
    Return "default" if "key" is not present in
    the dictionary.
    """
    from django.conf import settings

    config_dict = getattr(settings, 'IMPROVED_PERMISSIONS_SETTINGS', None)
    if config_dict:
        if key in config_dict:
            return config_dict[key]
    return default


def dip_cache():
    """
    Proxy method used to get the cache
    object belonging to the DIP.
    """
    from django.core.cache import caches
    return caches[get_config('CACHE', 'default')]


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
        Permission.objects.count()
    except:  # pragma: no cover
        return

    # Remove all references about previous
    # role classes and erase all cache.
    RoleManager.cleanup()
    dip_cache().clear()

    # Looking for Role classes in "roles.py".
    module = get_config('MODULE', 'roles')
    for app in settings.INSTALLED_APPS:
        try:
            mod = import_module('%s.%s' % (app, module))
            rc_list = [obj[1] for obj in inspect.getmembers(mod, is_role)]
            for roleclass in rc_list:
                RoleManager.register_role(roleclass)
        except ImportError:
            pass

    # Clear the cache again after
    # all registrations.
    dip_cache().clear()


def get_roleclass(role_class):
    """
    Get the role class signature
    by string or by itself.
    """
    from improved_permissions.roles import RoleManager
    roles_list = RoleManager.get_roles()

    if isinstance(role_class, str):
        # Trying to get the role class
        # via string representation.
        for role in roles_list:
            if role.get_class_name() == role_class:
                return role

    elif role_class in roles_list:
        # Already a Role class.
        return role_class

    raise RoleNotFound(
        "'%s' is not a registered role class." % role_class
    )


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

    # Getting the list of all permissions
    # from the cache.
    all_perms = dip_cache().get('permissions')

    # Build the cache dictionary for all
    # permissions if is not ready yet.
    if all_perms is None:
        all_perms = dict()
        query = Permission.objects.select_related('content_type').all()
        for perm_obj in query:
            key = permission_to_string(perm_obj)
            all_perms[key] = perm_obj
        dip_cache().set('permissions', all_perms)

    # Get the Permission instance
    # from the cache dictionary.
    try:
        return all_perms[perm]
    except KeyError:
        raise AttributeError


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
    options = getattr(model, 'RoleOptions', None)
    if options:
        parents_list = getattr(options, 'permission_parents', None)
        if parents_list:
            for parent in parents_list:
                parent_attr = getattr(model, parent, None)
                if parent_attr:
                    result.append(parent_attr)
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
    options = getattr(model, 'RoleOptions', None)
    if options:
        unique = getattr(options, 'unique_together', None)
        if unique:
            if isinstance(unique, bool):
                return unique
            raise ImproperlyConfigured('The field "unique_together" of "%s" must '
                                       'be a bool value.' % (str(model)))
    return False


def inherit_check(role, permission):
    """
    Check if the role class has the following
    permission in inherit mode.
    """
    from improved_permissions.roles import ALLOW_MODE

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
    ur_list = UserRole.objects.filter(content_type=ct_obj.id, object_id=instance.id)

    for ur_obj in ur_list:
        # Cleaning the cache system.
        delete_from_cache(ur_obj.user, instance)
        ur_obj.delete()


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
            post_delete.connect(cleanup_handler, sender=model, dispatch_uid=str(model))


def check_my_model(role, obj):
    """
    if both are provided, check if obj
    (instance or model class) belongs
    to the role class.
    """
    if role and obj and not role.is_my_model(obj):
        model_name = obj._meta.model  # pylint: disable=protected-access
        raise NotAllowed('The model "%s" does not belong to the Role "%s"'
                         '.' % (model_name, role.get_verbose_name()))


def generate_cache_key(user, obj=None):
    """
    Generate a md5 digest based on the
    string representation of the user
    and the object passed via arguments.
    """
    from hashlib import md5

    key = md5()
    key.update(str(user).encode('utf-8'))
    if obj:
        key.update(str(obj).encode('utf-8'))
    return key.hexdigest()


def delete_from_cache(user, obj=None):
    """
    Delete all permissions data from
    the cache about the user and the
    object passed via arguments.
    """

    key = generate_cache_key(user, obj)
    dip_cache().delete(key)


def get_from_cache(user, obj=None):
    """
    Get all permissions data about
    the user and the object passed
    via arguments e store it in
    the Django cache system.
    """
    from django.contrib.contenttypes.models import ContentType
    from improved_permissions.models import UserRole

    # Key preparation.
    key = generate_cache_key(user, obj)

    # Check for the cached data.
    data = dip_cache().get(key)
    if data is None:
        query = UserRole.objects.prefetch_related('accesses').filter(user=user)

        # Filtering by object.
        if obj:
            ct_obj = ContentType.objects.get_for_model(obj)
            query = query.filter(content_type=ct_obj.id).filter(object_id=obj.id)
        else:
            query = query.filter(content_type__isnull=True).filter(object_id__isnull=True)

        # Getting only the required values.
        query = query.values_list(
            'role_class',
            'accesses__permission',
            'accesses__access'
        )

        # Transform the query result into
        # a dictionary.
        data = dict()
        for item in query:
            perms_list = data.get(item[0], [])
            perms_list.append((item[1], item[2]))
            data[item[0]] = perms_list

        # Set the data to the cache.
        dip_cache().set(key, data)

    return data
