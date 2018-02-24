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

class Teacher(Role):
    verbose_name = "Teacher"
    models = [User]


class RoleClassTest(TestCase):
    """ role class tests """

    def setUp(self):
        RoleManager.cleanup()

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

        # Registering the role classes correctly
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Teacher)

        # Trying to register Advisor again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Advisor)

        # Trying to register Teacher again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Teacher)

        registered = [Advisor, Teacher]
        self.assertEqual(RoleManager.get_roles(), registered)


class ShortcutsTest(TestCase):
    """ test all functions in shortcuts """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Teacher)
        self.john = User.objects.create(username="john")
        self.bob = User.objects.create(username="bob")
        self.mike = User.objects.create(username="mike")
        self.julie = User.objects.create(username="julie")

    def test_assign_roles(self):
        """ test if the assignment methods work fine """
        shortcuts.assign_role(self.john, Teacher, self.bob)
        shortcuts.assign_role(self.mike, Teacher, self.bob)

        users_list = shortcuts.get_users_by_role(Teacher, self.bob)
        self.assertEqual(users_list, [self.john, self.mike])

    def test_assign_unique_roles(self):
        """ test if 'unique' attribute works fine """
        shortcuts.assign_role(self.john, Advisor, self.bob)

        users_list = shortcuts.get_users_by_role(Advisor, self.bob)
        self.assertEqual(users_list, [self.john])

        # Trying to add the role again using a Role with unique=True
        with self.assertRaises(exceptions.InvalidRoleAssignment):
            shortcuts.assign_role(self.mike, Advisor, self.bob)

    def _test_parents(self):

        shortcuts.assign_role(self.user1, Advisor, self.user2)
        rp = RolePermission.objects.get(pk=1)
        a = utils.get_permissions_parents(rp)
        print(a)
