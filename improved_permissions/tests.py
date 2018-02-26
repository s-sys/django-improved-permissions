""" permissions tests """
from django.contrib.auth.models import User
from django.test import TestCase

from improved_permissions import ALL_MODELS, Role, RoleManager, exceptions
from improved_permissions.shortcuts import (assign_permission, assign_role,
                                            assign_roles, get_users_by_role,
                                            has_permission, has_role,
                                            remove_role, remove_roles)


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
    deny = []


class Teacher(Role):
    verbose_name = "Teacher"
    models = [User]
    deny = ['auth.delete_user']


class Secretary(Role):
    verbose_name = "Secretary"
    models = [User]
    allow = ['auth.delete_user']


class SubCoordenator(Role):
    verbose_name = "SubCoordenator"
    models = ALL_MODELS
    inherit_allow = ['auth.change_user']


class Coordenator(Role):
    verbose_name = "Coordenator"
    models = ALL_MODELS
    inherit_deny = ['auth.change_user']


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
        RoleManager.register_role(Secretary)
        RoleManager.register_role(SubCoordenator)
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

        # Trying to assign a object role without object
        with self.assertRaises(exceptions.InvalidRoleAssignment):
            assign_role(self.john, Advisor)

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

    def test_has_permission(self):
        """ test if the has_permission method works fine """
        assign_role(self.john, Teacher, self.bob)
        self.assertTrue(has_permission(self.john, 'auth.add_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'auth.delete_user', self.bob))

        assign_role(self.mike, Secretary, self.bob)
        self.assertTrue(has_permission(self.mike, 'auth.delete_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'auth.add_user', self.bob))

        assign_role(self.bob, SubCoordenator)
        self.assertTrue(has_permission(self.bob, 'auth.change_user'))
        self.assertTrue(has_permission(self.bob, 'auth.change_user', self.julie))
        self.assertFalse(has_permission(self.bob, 'auth.add_user', self.julie))

        assign_role(self.julie, Coordenator)
        self.assertTrue(has_permission(self.julie, 'auth.add_user'))
        self.assertTrue(has_permission(self.julie, 'auth.add_user', self.bob))
        self.assertFalse(has_permission(self.julie, 'auth.change_user', self.bob))

    def test_remove_roles(self):
        """ test if the remove_roles method works fine """
        assign_role(self.john, Teacher, self.bob)
        remove_role(self.john, Teacher, self.bob)

        users_list = get_users_by_role(Teacher)
        self.assertEqual(users_list, [])

        assign_roles([self.john, self.mike], Teacher, self.bob)
        remove_roles([self.john, self.mike], Teacher)

        users_list = get_users_by_role(Teacher)
        self.assertEqual(users_list, [])

        assign_role(self.julie, Coordenator)
        self.assertTrue(has_permission(self.julie, 'auth.add_user'))
        remove_role(self.julie, Coordenator)
        self.assertFalse(has_permission(self.julie, 'auth.add_user'))

    def test_assign_permissions(self):
        """ test if the permissions assignment works fine """

        # Assign the role and try to use a permission denied by default.
        assign_role(self.john, Teacher, self.bob)
        assign_role(self.john, Teacher, self.julie)
        self.assertFalse(has_permission(self.john, 'auth.delete_user', self.bob))
        self.assertFalse(has_permission(self.john, 'auth.delete_user', self.julie))

        # Explicitly assign the permission using access=True and the object.
        assign_permission(self.john, Teacher, 'auth.delete_user', True, self.bob)

        # Result: Only the specified object was affected.
        self.assertTrue(has_permission(self.john, 'auth.delete_user', self.bob))
        self.assertFalse(has_permission(self.john, 'auth.delete_user', self.julie))

        # Assign the role and try to use a permission allowed by default
        assign_role(self.mike, Teacher, self.bob)
        assign_role(self.mike, Teacher, self.julie)
        self.assertTrue(has_permission(self.mike, 'auth.add_user', self.bob))
        self.assertTrue(has_permission(self.mike, 'auth.add_user', self.julie))

        # Explicitly assign the permission using access=False but without an object.
        assign_permission(self.mike, Teacher, 'auth.add_user', False)

        # Result: All the user's role instances were affected
        self.assertFalse(has_permission(self.mike, 'auth.add_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'auth.add_user', self.julie))
