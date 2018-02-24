""" permissions tests """
from django.contrib.auth.models import User
from django.test import TestCase

from improved_permissions import (ALL_MODELS, Role, RoleManager, exceptions,
                                  utils)
from improved_permissions.models import RolePermission
from improved_permissions.shortcuts import (assign_role, assign_roles,
                                            get_users_by_role, has_role)


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

class Coordenator(Role):
    verbose_name = "Coordenator"
    models = ALL_MODELS


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
        RoleManager.register_role(Coordenator)

        # Trying to register Advisor again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Advisor)

        # Trying to register Teacher again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Teacher)

        # Trying to register Coordenator again
        with self.assertRaises(exceptions.ImproperlyConfigured):
            RoleManager.register_role(Coordenator)

        registered = [Advisor, Teacher, Coordenator]
        self.assertEqual(RoleManager.get_roles(), registered)


class ShortcutsTest(TestCase):
    """ test all functions in shortcuts """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Teacher)
        RoleManager.register_role(Coordenator)
        self.john = User.objects.create(username="john")
        self.bob = User.objects.create(username="bob")
        self.mike = User.objects.create(username="mike")
        self.julie = User.objects.create(username="julie")

    def test_assign_roles(self):
        """ test if the assignment methods work fine """
        assign_roles([self.john, self.mike], Teacher, self.bob)

        users_list = get_users_by_role(Teacher, self.bob)
        self.assertEqual(users_list, [self.john, self.mike])

    def test_assign_roles_allmodels(self):
        """ test if the roles using ALL_MODELS work fine """
        assign_role(self.john, Coordenator)

        # Trying to assign a non-object role using a object
        with self.assertRaises(exceptions.InvalidRoleAssignment):
            assign_role(self.john, Coordenator, self.bob)

    def test_assign_roles_unique(self):
        """ test if 'unique' attribute works fine """
        assign_role(self.john, Advisor, self.bob)
        assign_role(self.john, Advisor, self.julie)

        # Trying to add the role again using a Role with unique=True
        with self.assertRaises(exceptions.InvalidRoleAssignment):
            assign_role(self.mike, Advisor, self.bob)

        # Trying to add the role again using a Role with unique=True
        with self.assertRaises(exceptions.InvalidRoleAssignment):
            assign_role(self.mike, Advisor, self.julie)
        
        users_list = get_users_by_role(Advisor)
        self.assertEqual(users_list, [self.john])

    def test_has_role(self):
        """ test if has_role method works fine """
        assign_role(self.john, Coordenator)
        self.assertTrue(has_role(self.john, Coordenator))
