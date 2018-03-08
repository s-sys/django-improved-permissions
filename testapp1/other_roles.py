""" testapp1 another role module """
from improved_permissions.roles import ALL_MODELS, Role


class AnotherRole(Role):
    verbose_name = "Another Role"
    models = ALL_MODELS
    deny = []
    inherit_deny = []
