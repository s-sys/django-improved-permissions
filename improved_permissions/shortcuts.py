""" permissions shortcuts """
# pylint: disable=too-many-lines
from django.contrib.contenttypes.models import ContentType

from improved_permissions import getters
from improved_permissions.exceptions import (InvalidPermissionAssignment,
                                             InvalidRoleAssignment)
from improved_permissions.models import RolePermission, UserRole
from improved_permissions.roles import ALL_MODELS
from improved_permissions.utils import (check_my_model, delete_from_cache,
                                        get_from_cache, get_parents,
                                        get_roleclass, inherit_check,
                                        is_unique_together,
                                        string_to_permission)


def get_user(role_class=None, obj=None):
    return getters.get_user(role_class, obj)


def get_users(role_class=None, obj=None):
    return getters.get_users(role_class, obj)


def get_objects(user, role_class=None, model=None):
    return getters.get_objects(user, role_class, model)


def has_role(user, role_class=None, obj=None):
    """
    Check if the "user" has any role
    attached to him.

    If "role_class" is provided, only
    this role class will be counted.

    If "obj" is provided, the search is
    refined to look only at that object.
    """

    query = UserRole.objects.filter(user=user)
    role = None

    if role_class:
        # Filtering by role class.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name(), user=user)

    if obj:
        # Filtering by object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    return query.count() > 0


def get_role(user, obj=None):
    """
    Proxy method to be used when you sure that
    will have only one role class attached.
    """
    return get_roles(user, obj)[0]


def get_roles(user, obj=None):
    """
    Return a list of role classes
    that is attached to "user".

    If "obj" is provided, the object
    must be attached as well.
    """
    query = UserRole.objects.filter(user=user)
    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Transform the string representations
    # into role classes and return as list.
    return [get_roleclass(ur_obj.role_class) for ur_obj in query]


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


def has_permission(user, permission, obj=None):
    """
    Return True if the "user" has the "permission".
    """
    perm_obj = string_to_permission(permission)
    if obj:
        stack = list()
        stack.append(obj)
        while stack:
            # Getting the dictionary of permissions
            # from the cache.
            current_obj = stack.pop(0)
            roles_list = get_from_cache(user, current_obj)
            for role_s, perm_list in roles_list:

                # Check for permissions.
                for perm_tuple in perm_list:
                    if perm_tuple[0] == perm_obj.id:
                        return perm_tuple[1]

                # Now, we are in inherit mode.
                # We need to check if the Role
                # allows the inherit.
                return inherit_check(get_roleclass(role_s), permission)

            # Try to look even further
            # for possible parent fields.
            parents_list = get_parents(current_obj)
            for parent in parents_list:
                stack.append(parent)

    # If nothing was found or the obj was
    # not provided, try now for roles with
    # "models" = ALL_MODELS.
    roles_list = get_from_cache(user)
    for role_s, perm_list in roles_list:

        # Check for permissions.
        for perm_tuple in perm_list:
            if perm_tuple[0] == perm_obj.id:
                return perm_tuple[1]

        # Now, we are in inherit mode.
        # We need to check if the Role
        # allows the inherit.
        return inherit_check(get_roleclass(role_s), permission)

    # If all fails and the user does not have
    # a role class with "ALL_MODELS", we finnaly
    # deny the permission.
    return False


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
