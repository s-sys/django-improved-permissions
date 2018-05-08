""" permissions templatetags """
from django import template

from improved_permissions.exceptions import NotAllowed
from improved_permissions.shortcuts import get_role as alias_get_role
from improved_permissions.shortcuts import has_permission

register = template.Library()


@register.simple_tag
def has_perm(user, permission, obj=None, persistent=None):
    """Adapts has_permission shortcut into a templatetag."""
    any_object = False

    # Checking the any_object kwarg.
    if obj and isinstance(obj, str) and obj == 'any':
        any_object = True
        obj = None

    # Checking the persistent kwarg.
    if persistent and isinstance(persistent, str):
        if persistent == 'persistent':
            persistent = True
        elif persistent == 'non-persistent':
            persistent = False
        else:
            raise NotAllowed(
                "Use 'persistent' or 'non-persistent' on Persistent Mode."
            )
    else:
        persistent = None

    # Return the default behavior of the shortcut.
    return has_permission(user, permission, obj, any_object, persistent)


@register.filter
def get_role(user, obj=None):
    return alias_get_role(user, obj).get_verbose_name()
