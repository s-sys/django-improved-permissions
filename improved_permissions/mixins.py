""" permissions mixins """
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models

from improved_permissions.shortcuts import assign_role as alias_assign_role
from improved_permissions.shortcuts import assign_roles as alias_assign_roles
from improved_permissions.shortcuts import get_users as alias_get_users
from improved_permissions.shortcuts import \
    get_users_by_role as alias_get_users_by_role
from improved_permissions.shortcuts import \
    has_permission as alias_has_permission
from improved_permissions.shortcuts import has_role as alias_has_role
from improved_permissions.shortcuts import remove_role as alias_remove_role
from improved_permissions.shortcuts import remove_roles as alias_remove_roles


class RoleMixin(models.Model):
    """
    RoleMixin

    This mixin is a helper to be attached
    in any model that heavily use the methods
    in the shortcuts module.

    All shortcuts become methods of the model
    omitting the "obj" argument, using itself
    to fill it.
    """
    class Meta:
        abstract = True

    def has_role(self, role_class):
        return alias_has_role(role_class, self)

    def get_users(self):
        return alias_get_users(self)

    def get_users_by_role(self, role_class):
        return alias_get_users_by_role(role_class, self)

    def assign_role(self, user, role_class):
        return alias_assign_role(user, role_class, self)

    def assign_roles(self, users_list, role_class):
        return alias_assign_roles(users_list, role_class, self)

    def remove_role(self, user, role_class):
        return alias_remove_role(user, role_class, self)

    def remove_roles(self, users_list, role_class):
        return alias_remove_roles(users_list, role_class, self)

    def has_permission(self, user, permission):
        return alias_has_permission(user, permission, self)


class PermissionMixin(object):
    """
    PermissionMixin

    This mixin helps the class-based views
    to secure them based in permissions.
    """
    permission_string = ""
    permission_object = None

    def get_permission_string(self):
        if self.permission_string != "":
            return self.permission_string

        raise ImproperlyConfigured()

    def get_permission_object(self):
        if self.permission_object:
            return self.permission_object

        elif hasattr(self, 'object'):
            return self.object

        raise ImproperlyConfigured()

    def check_permission(self):
        return alias_has_permission(
            self.request.user,
            self.get_permission_string(),
            self.get_permission_object()
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.check_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
