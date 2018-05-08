"""checkers functions"""
from django.contrib.contenttypes.models import ContentType

from improved_permissions.exceptions import NotAllowed
from improved_permissions.models import UserRole
from improved_permissions.utils import (check_my_model, get_config,
                                        get_from_cache, get_parents,
                                        get_roleclass, inherit_check,
                                        string_to_permission)


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


def has_permission(user, permission, obj=None, any_object=False, persistent=None):
    """
    Return True if the "user" has the "permission".
    """
    perm_obj = string_to_permission(permission)

    # Checking the 'any_object' bypass kwarg.
    if any_object and obj:
        raise NotAllowed(
            "You cannot provide an object and use any_object=True at same time."
        )

    # Checking the 'persistent' bypass kwarg.
    if not isinstance(persistent, bool):
        persistent = get_config('PERSISTENT', False)

    stack = list()
    stack.append(obj)
    while stack:
        # Getting the permissions list of the first
        # role class based on their role ranking.
        current_obj = stack.pop(0)
        result_tuple = get_from_cache(user, current_obj, any_object)

        if result_tuple:
            # Checking now for database results.
            result = None
            for perm_tuple in result_tuple[1]:
                if perm_tuple[0] == perm_obj.id:
                    result = perm_tuple[1]
                    break

            # If nothing was found, check for inherit results.
            if result is None:
                result = inherit_check(result_tuple[0], permission)

            # We got a result.
            # Now checking for persistent mode.
            if result or not persistent:
                return result

        # Try to look even further
        # for possible parent fields.
        parents_list = get_parents(current_obj)
        for parent in parents_list:
            stack.append(parent)

        # Force another iteration in case of any permission was
        # found using object-related roles. Using 'None', we
        # check now for ALL_MODELS roles.
        if obj and not stack:
            stack.append(None)
            obj = None

    # If all fails and the user does not have
    # a role class with "ALL_MODELS", we finally
    # deny the permission.
    return False
