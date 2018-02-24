""" permissions shortcuts """
from django.contrib.contenttypes.models import ContentType

from improved_permissions import exceptions
from improved_permissions.models import RolePermission
from improved_permissions.roles import ALL_MODELS
from improved_permissions.utils import get_roleclass


def has_role(user, role_class, obj=None):
    """
    Check if the "user" has the specific
    role.
    If "obj" is provided, the search is
    refined to look only at that object.
    """
    role = get_roleclass(role_class)
    query = RolePermission.objects.filter(role_class=role.get_class_name(), user=user)

    if role.is_my_model(obj):
        # Example: If "user" is an "Author" of "Book A".
        ct_obj = ContentType.objects.get_for_model(obj)
        query.filter(content_type=ct_obj.id, object_id=obj.id)

    return query.count() > 0


def get_users_by_role(role_class, obj=None):
    """
    Return the a list of Users instances
    based on the Role class provided
    by "role_class".

    If "obj" is provided, get the Users
    who has the Role class and the object.
    """
    role = get_roleclass(role_class)
    query = RolePermission.objects.filter(role_class=role.get_class_name())

    if role.is_my_model(obj):
        # Example: Get all "Author"s from "Book A".
        ct_obj = ContentType.objects.get_for_model(obj)
        query.filter(content_type=ct_obj.id, object_id=obj.id)

    elif not obj and role.models == ALL_MODELS:
        # Example: Get all Coordenators (non-object attached roles).
        query.filter(content_type__isnull=True, object_id__isnull=True)

    elif obj == ALL_MODELS:
        # Example: Get all "Author"s from all "Books".
        pass
    else:
        # Wrong combination of arguments.
        raise exceptions.BadRoleArguments()

    # QuerySet to users list.
    return [rp.user for rp in query]


def assign_role(user, role_class, obj=None):
    """
    Proxy method to be used for one
    User instance.
    """
    assign_roles([user], role_class, obj)


def assign_roles(users_list, role_class, obj=None):
    """
    Create a RolePermission object in the database
    referencing the followling role_class to the
    user.
    """
    role = get_roleclass(role_class)
    models = role.get_models()

    # If no object is provided but the role needs specific models.
    if not obj and role.models != ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    # If a object is provided but the role does not needs a object.
    if obj and role.models == ALL_MODELS:
        raise exceptions.InvalidRoleAssignment()

    # If a object is provided but the role does not register for THAT specific model.
    if obj._meta.model not in models:
        raise exceptions.InvalidRoleAssignment()

    if role.unique is True:
        # If the role is marked as unique but multiple users is provided.
        if len(users_list) > 1:
            raise exceptions.InvalidRoleAssignment()

        # If the role is marked as unique but already has an user attached.
        has_user = get_users_by_role(role, obj)
        if has_user:
            raise exceptions.InvalidRoleAssignment()

    perms_list = list()
    users_set = set(users_list)
    for user in users_set:
        rp_instance = RolePermission(role_class=role.get_class_name(), user=user)
        if obj:
            rp_instance.obj = obj
        perms_list.append(rp_instance)
    RolePermission.objects.bulk_create(perms_list)


def has_permission(user, permission, obj=None):
    """
    TODO
    """
    return False


def get_users_by_permission(permission, obj=None):
    """
    TODO
    """
    return list()
