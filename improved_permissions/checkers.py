"""checkers functions"""
from django.contrib.contenttypes.models import ContentType

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


def has_permission(user, permission, obj=None):
    """
    Return True if the "user" has the "permission".
    """
    persistent = get_config('PERSISTENT', False)

    perm_obj = string_to_permission(permission)
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
                    result = perm_tuple[1]

                    # We got a result.
                    # Now checking for persist mode.
                    if persistent and not result:
                        break
                    else:
                        return result

            # Now, we are in inherit mode. We need to check
            # if the Role allows the inherit.
            inherit = inherit_check(get_roleclass(role_s), permission)

            # Checking for persist mode once again.
            if persistent and not inherit:
                pass
            else:
                return inherit

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
