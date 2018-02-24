""" permissions tests """
from django.test import TestCase

from improved_permissions import exceptions, roles


class NoVerboseNameRole(roles.Role):
    pass

class NoModelRole1(roles.Role):
    verbose_name = "Role"

class NoModelRole2(roles.Role):
    verbose_name = "Role"
    models = None

class NoModelRole3(roles.Role):
    verbose_name = "Role"
    models = [1, 2]


class PermissionsTest(TestCase):

    def test_incorrect_implementations(self):
        """ test all exceptions on validate method """

        # Role class without "verbose_name"
        with self.assertRaises(exceptions.ImproperlyConfigured):
            roles.Role.register_role(NoVerboseNameRole)

        # Role class without "models"
        with self.assertRaises(exceptions.ImproperlyConfigured):
            roles.Role.register_role(NoModelRole1)

        # Role class with "models" as no list
        with self.assertRaises(exceptions.ImproperlyConfigured):
            roles.Role.register_role(NoModelRole2)

        # Role class with "models" as list of non-Models
        with self.assertRaises(exceptions.ImproperlyConfigured):
            roles.Role.register_role(NoModelRole3)
