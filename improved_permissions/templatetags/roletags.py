""" permissions templatetags """
from django import template

from improved_permissions.shortcuts import get_role as alias_get_role
from improved_permissions.shortcuts import has_permission

register = template.Library()


@register.simple_tag
def has_perm(user, permission, obj=None, persistent=None):
    if obj and isinstance(obj, str) and obj == 'any':
        return has_permission(user, permission, obj=None, any_object=True, persistent=persistent)
    return has_permission(user, permission, obj, any_object=False, persistent=persistent)


@register.filter
def get_role(user, obj=None):
    return alias_get_role(user, obj).get_verbose_name()
