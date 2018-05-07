""" permissions shortcuts """
from improved_permissions import assignments, checkers, getters


def get_user(role_class=None, obj=None):
    return getters.get_user(role_class, obj)


def get_users(role_class=None, obj=None):
    return getters.get_users(role_class, obj)


def get_objects(user, role_class=None, model=None):
    return getters.get_objects(user, role_class, model)


def get_role(user, obj=None):
    return getters.get_role(user, obj)


def get_roles(user, obj=None):
    return getters.get_roles(user, obj)


def has_role(user, role_class=None, obj=None):
    return checkers.has_role(user, role_class, obj)


def has_permission(user, permission, obj=None, any_object=False, persistent=None):
    return checkers.has_permission(user, permission, obj, any_object, persistent)


def assign_role(user, role_class, obj=None):
    assignments.assign_role(user, role_class, obj)


def assign_roles(users_list, role_class, obj=None):
    assignments.assign_roles(users_list, role_class, obj)


def remove_role(user, role_class=None, obj=None):
    assignments.remove_role(user, role_class, obj)


def remove_roles(users_list, role_class=None, obj=None):
    assignments.remove_roles(users_list, role_class, obj)


def remove_all(role_class=None, obj=None):
    assignments.remove_all(role_class, obj)


def assign_permission(user, role_class, permission, access, obj=None):
    assignments.assign_permission(user, role_class, permission, access, obj)
