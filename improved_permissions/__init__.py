""" permissions init module """
from improved_permissions.roles import Role, RoleManager, ALL_MODELS, ALLOW_MODE, DENY_MODE # pylint: disable=unused-import

default_app_config = 'improved_permissions.apps.ImprovedPermissionsConfig'  # pylint: disable=invalid-name

__all__ = ['RoleManager', 'Role', 'ALL_MODELS', 'ALLOW_MODE', 'DENY_MODE']
