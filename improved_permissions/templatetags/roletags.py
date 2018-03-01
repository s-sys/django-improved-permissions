""" permissions templatetags """
from django import template

from improved_permissions.shortcuts import get_role as alias_get_role
from improved_permissions.shortcuts import has_permission

register = template.Library()


@register.simple_tag
def has_perm(user, permission, obj=None):
    return has_permission(user, permission, obj)


@register.filter
def get_role(user, obj=None):
    return alias_get_role(user, obj).get_verbose_name()
