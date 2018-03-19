""" RoleManager tests """
from django.test import TestCase

from improved_permissions.exceptions import (ImproperlyConfigured,
                                             InvalidRoleAssignment)
from improved_permissions.roles import ALL_MODELS, Role, RoleManager
from improved_permissions.utils import autodiscover, get_config
from testapp1.models import MyUser
from testapp1.other_roles import AnotherRole
from testapp1.roles import Advisor


class NoVerboseNameRole(Role):
    pass


class NoModelRole1(Role):
    verbose_name = "Role"


class NoModelRole2(Role):
    verbose_name = "Role"
    models = None


class NoModelRole3(Role):
    verbose_name = "Role"
    models = [1, 2]


class NoAllowDenyRole(Role):
    verbose_name = "Role"
    models = [MyUser]


class WrongDenyRole(Role):
    verbose_name = "Role"
    models = ['testapp1.MyUser']
    deny = 'I am not a list'


class WrongPermissionRole(Role):
    verbose_name = "Role"
    models = [MyUser]
    deny = ['I am not a permission.']


class RoleManagerTest(TestCase):
    """ RoleManager class tests """

    def setUp(self):
        RoleManager.cleanup()

    def test_another_module(self):
        """ test if the config dictionary works fine """

        # Testing module name.
        new_ipc = {'MODULE': 'other_roles'}
        with self.settings(IMPROVED_PERMISSIONS_SETTINGS=new_ipc):
            autodiscover()
            roles_list = RoleManager.get_roles()
            self.assertEqual(roles_list, [AnotherRole])

        # Testing the case if the dictionary does not exists.
        with self.settings(IMPROVED_PERMISSIONS_SETTINGS=None):
            self.assertEqual(get_config('CACHE', 'new_default'), 'new_default')
            self.assertEqual(get_config('MODULE', 'new_roles'), 'new_roles')

        # Test the default cache prefix key
        self.assertEqual(get_config('CACHE_PREFIX_KEY', 'prefix'), 'dip-')

        # Test the new cache prefix key via settings
        new_ipc = {'CACHE_PREFIX_KEY': 'django-improved-permissions-'}
        with self.settings(IMPROVED_PERMISSIONS_SETTINGS=new_ipc):
            self.assertEqual(get_config('CACHE_PREFIX_KEY', 'prefix'), 'django-improved-permissions-')

    def test_incorrect_implementations(self):
        """ test all exceptions on validate method """

        # Trying to instantiate RoleManager.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager()

        # Trying to register a random object.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(object)

        # Role class without "verbose_name".
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(NoVerboseNameRole)

        # Role class without "models".
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(NoModelRole1)

        # Role class with "models" as no list.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(NoModelRole2)

        # Role class with "models" as list of random things.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(NoModelRole3)

        # Role class without any deny or allow.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(NoAllowDenyRole)

        # Role class with "deny" defined incorrectly.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(WrongDenyRole)

        # Role class with "deny" defined incorrectly.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(WrongPermissionRole)

        # Registering the role classes correctly.
        RoleManager.register_role(Advisor)

        # Trying to register Advisor again.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(Advisor)

        # Checking list.
        self.assertEqual(RoleManager.get_roles(), [Advisor])
