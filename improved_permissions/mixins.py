""" permissions mixins """
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models

from improved_permissions import shortcuts


class UserRoleMixin(models.Model):
    """
    UserRoleMixin

    This mixin is a helper to be attached
    in the User model in order to use the
    most of the methods in the shortcuts
    module.
    """
    class Meta:
        abstract = True

    def has_role(self, role_class, obj=None):
        return shortcuts.has_role(self, role_class, obj)

    def get_objects(self, role_class=None):
        return shortcuts.get_objects(self, role_class)

    def get_permissions(self, role_class, obj=None):
        return shortcuts.get_permissions(self, role_class, obj)

    def assign_role(self, role_class, obj=None):
        return shortcuts.assign_role(self, role_class, obj)

    def remove_role(self, role_class, obj=None):
        return shortcuts.remove_role(self, role_class, obj)

    def has_permission(self, permission, obj=None):
        return shortcuts.has_permission(self, permission, obj)


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

    def get_users(self):
        return shortcuts.get_users(self)

    def get_users_by_role(self, role_class):
        return shortcuts.get_users_by_role(role_class, self)

    def assign_role(self, user, role_class):
        return shortcuts.assign_role(user, role_class, self)

    def assign_roles(self, users_list, role_class):
        return shortcuts.assign_roles(users_list, role_class, self)

    def remove_role(self, user, role_class):
        return shortcuts.remove_role(user, role_class, self)

    def remove_roles(self, users_list, role_class):
        return shortcuts.remove_roles(users_list, role_class, self)


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

        elif hasattr(self, 'get_object'):
            return self.get_object()

        raise ImproperlyConfigured()

    def check_permission(self):
        return shortcuts.has_permission(
            self.request.user,
            self.get_permission_string(),
            self.get_permission_object()
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.check_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
