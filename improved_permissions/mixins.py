""" permissions mixins """
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import models

from improved_permissions import shortcuts
from improved_permissions.models import UserRole


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

    def has_role(self, role_class=None, obj=None):
        return shortcuts.has_role(self, role_class, obj)

    def get_role(self, obj=None):
        return shortcuts.get_role(self, obj)

    def get_roles(self, obj=None):
        return shortcuts.get_roles(self, obj)

    def get_objects(self, role_class=None, model=None):
        return shortcuts.get_objects(self, role_class, model)

    def get_permissions(self, role_class, obj=None):
        return shortcuts.get_permissions(self, role_class, obj)

    def assign_role(self, role_class, obj=None):
        return shortcuts.assign_role(self, role_class, obj)

    def remove_role(self, role_class=None, obj=None):
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

    roles = GenericRelation(UserRole)

    class Meta:
        abstract = True

    def get_user(self, role_class=None):
        return shortcuts.get_user(role_class, self)

    def get_users(self, role_class=None):
        return shortcuts.get_users(role_class, self)

    def has_role(self, user, role_class=None):
        return shortcuts.has_role(user, role_class, self)

    def get_role(self, user):
        return shortcuts.get_role(user, self)

    def get_roles(self, user):
        return shortcuts.get_roles(user, self)

    def assign_role(self, user, role_class):
        return shortcuts.assign_role(user, role_class, self)

    def assign_roles(self, users_list, role_class):
        return shortcuts.assign_roles(users_list, role_class, self)

    def remove_role(self, user, role_class=None):
        return shortcuts.remove_role(user, role_class, self)

    def remove_roles(self, users_list, role_class=None):
        return shortcuts.remove_roles(users_list, role_class, self)


class PermissionMixin(object):
    """
    PermissionMixin

    This mixin helps the class-based views
    to secure them based in permissions.
    """
    permission_string = ""

    def get_permission_string(self):
        if self.permission_string != "":
            return self.permission_string

        raise ImproperlyConfigured(
            "Provide a 'permission_string' attribute."
        )

    def get_permission_object(self):
        if hasattr(self, 'permission_object'):
            return self.permission_object

        elif hasattr(self, 'object') and self.object is not None:
            return self.object

        elif hasattr(self, 'get_object'):
            return self.get_object()

        raise ImproperlyConfigured(
            "Provide a 'permission_object' attribute or implement "
            "a 'get_permission_object' method."
        )

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
