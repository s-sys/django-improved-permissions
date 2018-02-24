""" permissions shortcuts """
from improved_permissions.models import RolePermission
from improved_permissions.utils import get_roleclass_by_name


def has_role(user, role_class, obj=None):
    return False


def has_permission(user, permission, obj=None):
    return False


def get_users_by_role(role_class):
    return list()


def get_users_by_permission(permission, obj=None):
    return list()


def assign_role(user, role_class, obj=None):
    assign_roles([user], role_class, obj)


def assign_roles(users_list, role_class, obj=None):
    role = get_roleclass_by_name(role_class)
    models = role.get_models()

    if not obj and role.models != role.ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    if obj and role.models == role.ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    if obj._meta.model not in role.get_models():
        raise exceptions.InvalidRoleAssignment()

    perms_list = list()
    users_set = set(users_list)
    for user in users_set:
        perms_list.append(RolePermission(role_class=role.get_class_name(), user=user, obj=obj)
    RolePermission.objects.bulk_create(perms_list)
