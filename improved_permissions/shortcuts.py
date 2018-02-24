""" permissions shortcuts """
from improved_permissions import exceptions
from improved_permissions.models import RolePermission
from improved_permissions.roles import ALL_MODELS
from improved_permissions.utils import get_roleclass_by_name


def has_role(user, role_class, obj=None):
    return False


def has_permission(user, permission, obj=None):
    return False


def get_users_by_role(role_class, obj=None):
    role = get_roleclass_by_name(role_class)
    query = RolePermission.objects.filter(role_class=role)
    if role.is_my_model(obj):  # get all authors from Book A
        query.filter(obj=obj)
    elif not obj and role.models == ALL_MODELS:  # get all "super" users (non object related roles)
        query.filter(obj__isnull=True)
    elif obj == ALL_MODELS: # get all authors from all Books
        pass
    else:
        raise exceptions.BadRoleArguments()

    return list(query.values('user'))


def get_users_by_permission(permission, obj=None):
    return list()


def assign_role(user, role_class, obj=None):
    assign_roles([user], role_class, obj)


def assign_roles(users_list, role_class, obj=None):
    role = get_roleclass_by_name(role_class)
    models = role.get_models()

    if not obj and role.models != ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    if obj and role.models == ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    if obj._meta.model not in models:
        raise exceptions.InvalidRoleAssignment()

    if obj and role.models == ALL_MODELS:
        obj = 

    perms_list = list()
    users_set = set(users_list)
    for user in users_set:
        perms_list.append(RolePermission(role_class=role.get_class_name(), user=user, obj=obj))
    RolePermission.objects.bulk_create(perms_list)
