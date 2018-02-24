""" permissions tests """
from django.contrib.auth.models import User
from django.test import TestCase

from improved_permissions import (Role, RoleManager, exceptions, shortcuts,
                                  utils)
from improved_permissions.models import RolePermission


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

class Advisor(Role):
    verbose_name = "Advisor"
    models = [User]
    unique = True


class RoleClassTest(TestCase):
    """ role class tests """

    def test_incorrect_implementations(self):
        """ test all exceptions on validate method """

        # Role class without "verbose_name"
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(NoVerboseNameRole)

        # Role class without "models"
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(NoModelRole1)

        # Role class with "models" as no list
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(NoModelRole2)

        # Role class with "models" as list of non-Models
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(NoModelRole3)

        # Registering Role class correctly
        RoleManager.register_role(Advisor)

        # Trying to register again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Advisor)


class ShortcutsTest(TestCase):
    """ test all functions in shortcuts """

    def setUp(self):
        self.user1 = User.objects.create(username="john")
        self.user2 = User.objects.create(username="bob")
        self.user3 = User.objects.create(username="mike")
        self.user4 = User.objects.create(username="julie")

    def test_assign_roles(self):
        """ test if the assignment methods work fine """

        shortcuts.assign_role(self.user1, Advisor, self.user2)

        users_list = shortcuts.get_users_by_role(Advisor, self.user2)
        self.assertEqual(users_list, [self.user1])

    def test_parents(self):

        shortcuts.assign_role(self.user1, Advisor, self.user2)
        rp = RolePermission.objects.get(pk=1)
        a = utils.get_permissions_parents(rp)
        print(a)
