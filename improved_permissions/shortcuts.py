""" permissions shortcuts """
from django.contrib.contenttypes.models import ContentType

from improved_permissions import ALL_MODELS, exceptions
from improved_permissions.models import RolePermission, UserRole
from improved_permissions.utils import (get_parents, get_roleclass,
                                        inherit_check, string_to_permission)


def has_role(user, role_class, obj=None):
    """
    Check if the "user" has the specific
    role.
    If "obj" is provided, the search is
    refined to look only at that object.
    """
    role = get_roleclass(role_class)
    query = UserRole.objects.filter(role_class=role.get_class_name(), user=user)

    if obj and role.is_my_model(obj):
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
    query = UserRole.objects.filter(role_class=role.get_class_name())

    if not obj and role.models == ALL_MODELS:
        # Example: Get all "Coordenators" (non-object roles).
        query = query.filter(content_type__isnull=True, object_id__isnull=True)
    elif obj and role.is_my_model(obj):
        # Example: Get all "Authors" from "Book A".
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)
    else:
        # Example: Get all "Authors" from all "Books".
        # Its possible to have duplicates in
        # this case, so we apply distinct here.
        # PostgreSQL only
        # query = query.distinct('user')
        # TODO
        return list(set([rp.user for rp in query]))
        # TODO

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
    if obj and obj._meta.model not in models:
        raise exceptions.InvalidRoleAssignment()

    if role.unique is True:
        # If the role is marked as unique but multiple users is provided.
        if len(users_list) > 1:
            raise exceptions.InvalidRoleAssignment()

        # If the role is marked as unique but already has an user attached.
        has_user = get_users_by_role(role, obj)
        if has_user:
            raise exceptions.InvalidRoleAssignment()

    users_set = set(users_list)
    for user in users_set:
        ur_instance = UserRole(role_class=role.get_class_name(), user=user)
        if obj:
            ur_instance.obj = obj
        ur_instance.save()


def has_permission(user, permission, obj=None):
    """
    Return True if the "user" has the "permission".
    """
    perm_obj = string_to_permission(permission)

    if obj:  # pylint: disable=too-many-nested-blocks
        stack = list()
        stack.append(obj)
        while stack:
            # Getting the UserRole for the current object.
            current_obj = stack.pop(0)
            ct_obj = ContentType.objects.get_for_model(current_obj)
            roles_list = (UserRole.objects
                          .filter(object_id=current_obj.id)
                          .filter(content_type=ct_obj.id)
                          .filter(user=user))

            for role_obj in roles_list:
                # Common search for the permission object
                perm_access = RolePermission.objects.get(role=role_obj, permission=perm_obj)
                if perm_access.access is True:
                    return True

                if current_obj != obj:
                    # Now, we are in inherit mode.
                    # We need to check if the Role
                    # allows the inherit.
                    valid, result = inherit_check(role_obj, permission)
                    if valid:
                        return result

            # If roles_list was empty or a deny
            # was found, try to look even futher
            # for possible parent fields.
            if not roles_list:
                parents_list = get_parents(current_obj)
                for parent in parents_list:
                    stack.append(parent)

    # If nothing was found or the obj was
    # not provided, try now for roles with
    # "models" = ALL_MODELS.
    allmodels_list = (UserRole.objects
                      .filter(content_type__isnull=True)
                      .filter(object_id__isnull=True)
                      .filter(user=user))
    for role_obj in allmodels_list:
        valid, result = inherit_check(role_obj, permission)
        if valid:
            return result

    # If all fails and the user does not have
    # a role class with "ALL_MODELS", we finnaly
    # deny the permission.
    return False

# def get_users_by_permission(permission, obj=None):
