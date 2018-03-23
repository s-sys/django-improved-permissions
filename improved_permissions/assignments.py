"""assignments functions"""
from django.contrib.contenttypes.models import ContentType

from improved_permissions.exceptions import (InvalidPermissionAssignment,
                                             InvalidRoleAssignment)
from improved_permissions.getters import get_roles, get_users
from improved_permissions.models import RolePermission, UserRole
from improved_permissions.roles import ALL_MODELS
from improved_permissions.utils import (check_my_model, delete_from_cache,
                                        get_roleclass, is_unique_together,
                                        string_to_permission)


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
    users_set = set(users_list)
    role = get_roleclass(role_class)
    name = role.get_verbose_name()

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # If no object is provided but the role needs specific models.
    if not obj and role.models != ALL_MODELS:
        raise InvalidRoleAssignment(
            'The role "%s" must be assigned with a object.' % name
        )

    # If a object is provided but the role does not needs a object.
    if obj and role.models == ALL_MODELS:
        raise InvalidRoleAssignment(
            'The role "%s" must not be assigned with a object.' % name
        )

    # Check if the model accepts multiple roles
    # attached using the same User instance.
    if obj and is_unique_together(obj):
        for user in users_set:
            has_user = get_roles(user=user, obj=obj)
            if has_user:
                raise InvalidRoleAssignment(
                    'The user "%s" already has a role attached '
                    'to the object "%s".' % (user, obj)
                )

    if role.unique is True:
        # If the role is marked as unique but multiple users are provided.
        if len(users_list) > 1:
            raise InvalidRoleAssignment(
                'Multiple users were provided using "%s", '
                'but it is marked as unique.' % name
            )

        # If the role is marked as unique but already has an user attached.
        has_user = get_users(role_class=role, obj=obj)
        if has_user:
            raise InvalidRoleAssignment(
                'The object "%s" already has a "%s" attached '
                'and it is marked as unique.' % (obj, name)
            )

    for user in users_set:
        ur_instance = UserRole(role_class=role.get_class_name(), user=user)
        if obj:
            ur_instance.obj = obj
        ur_instance.save()

        # Cleaning the cache system.
        delete_from_cache(user, obj)


def assign_permission(user, role_class, permission, access, obj=None):
    """
    Assign a specific permission value
    to a given UserRole instance.
    The values used in this method overrides
    any configuration of "allow/deny" or
    "inherit_allow/inherit_deny".
    """
    role = get_roleclass(role_class)
    perm = string_to_permission(permission)
    query = UserRole.objects.filter(user=user, role_class=role.get_class_name())
    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    if not query:
        raise InvalidPermissionAssignment('No Role instance was affected.')

    for role_obj in query:
        perm_obj, created = RolePermission.objects.get_or_create(  # pylint: disable=W0612
            role=role_obj,
            permission=perm
        )
        perm_obj.access = bool(access)
        perm_obj.save()

        # Cleaning the cache system.
        delete_from_cache(user, role_obj.obj)


def remove_role(user, role_class=None, obj=None):
    """
    Proxy method to be used for one
    User instance.
    """
    remove_roles([user], role_class, obj)


def remove_roles(users_list, role_class=None, obj=None):
    """
    Delete all RolePermission objects in the database
    referencing the followling role_class to the
    user.
    If "obj" is provided, only the instances refencing
    this object will be deleted.
    """
    query = UserRole.objects.filter(user__in=users_list)
    role = None

    if role_class:
        # Filtering by role class.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())

    if obj:
        # Filtering by object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Cleaning the cache system.
    for user in users_list:
        delete_from_cache(user, obj)

    # Cleaning the database.
    query.delete()


def remove_all(role_class=None, obj=None):
    """
    Remove all roles of the project.

    If "role_class" is provided,
    only the roles of "role_class"
    will be affected.

    If "obj" is provided, only
    users for that object will
    lose the role.
    """
    query = UserRole.objects.all()
    role = None

    if role_class:
        # Filtering by role class.
        role = get_roleclass(role_class)
        query = UserRole.objects.filter(role_class=role.get_class_name())

    if obj:
        # Filtering by object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Cleaning the cache system.
    for role_obj in query:
        delete_from_cache(role_obj.user, role_obj.obj)

        # Cleaning the database.
        role_obj.delete()
