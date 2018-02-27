"""permissions exceptions"""


class ImproperlyConfigured(Exception):
    pass


class ParentNotFound(Exception):
    pass


class RoleNotFound(Exception):
    pass


class InvalidRoleAssignment(Exception):
    pass


class InvalidPermissionAssignment(Exception):
    pass


class NotAllowed(Exception):
    pass
