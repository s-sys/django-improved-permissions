""" permissions tests """
from django.test import TestCase

from improved_permissions.exceptions import (InvalidPermissionAssignment,
                                             InvalidRoleAssignment, NotAllowed)
from improved_permissions.roles import ALL_MODELS, Role, RoleManager
from improved_permissions.shortcuts import (assign_permission, assign_role,
                                            assign_roles, get_user, get_users,
                                            has_permission, has_role,
                                            remove_role, remove_roles)
from improved_permissions.templatetags.roletags import get_role as tg_get_role
from improved_permissions.templatetags.roletags import has_perm as tg_has_perm
from testapp1.models import Chapter, MyUser, UniqueTogether


class Advisor(Role):
    verbose_name = "Advisor"
    models = [MyUser]
    unique = True
    deny = []


class Teacher(Role):
    verbose_name = "Teacher"
    models = [MyUser]
    deny = ['testapp1.delete_user']


class Secretary(Role):
    verbose_name = "Secretary"
    models = [MyUser, UniqueTogether]
    allow = ['testapp1.delete_user']


class SubCoordenator(Role):
    verbose_name = "Sub Coordenator"
    models = ALL_MODELS
    inherit_allow = ['testapp1.change_user']


class Coordenator(Role):
    verbose_name = "Coordenator"
    models = ALL_MODELS
    inherit_deny = ['testapp1.change_user']


class UniqueOwner(Role):
    verbose_name = "Owner of Unique"
    models = [UniqueTogether]
    deny = []


class ShortcutsTest(TestCase):
    """ test all functions in shortcuts """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Teacher)
        RoleManager.register_role(Secretary)
        RoleManager.register_role(SubCoordenator)
        RoleManager.register_role(Coordenator)
        RoleManager.register_role(UniqueOwner)

        self.john = MyUser.objects.create(username="john")
        self.bob = MyUser.objects.create(username="bob")
        self.mike = MyUser.objects.create(username="mike")
        self.julie = MyUser.objects.create(username="julie")
        self.unique = UniqueTogether.objects.create(content='Some data')

    def test_assign_roles(self):
        """ test if the assignment methods work fine """
        assign_roles([self.john, self.mike], Teacher, self.bob)

        users_list = get_users(Teacher, self.bob)
        self.assertEqual(users_list, [self.john, self.mike])

        with self.assertRaises(NotAllowed):
            assign_role(self.john, Teacher, Chapter)

    def test_assign_roles_allmodels(self):
        """ test if the roles using ALL_MODELS work fine """
        assign_role(self.john, Coordenator)

        # Trying to assign a non-object role using a object
        with self.assertRaises(InvalidRoleAssignment):
            assign_role(self.john, Coordenator, self.bob)

        # Trying to assign a object role without object
        with self.assertRaises(InvalidRoleAssignment):
            assign_role(self.john, Advisor)

        users_list = get_users(Coordenator)
        self.assertEqual(users_list, [self.john])

    def test_assign_roles_unique(self):
        """ test if 'unique' attribute works fine """
        assign_role(self.john, Advisor, self.bob)
        assign_role(self.john, Advisor, self.julie)

        # Trying to assign the multiple roles using a Role with unique=True
        with self.assertRaises(InvalidRoleAssignment):
            assign_roles([self.john, self.mike], Advisor, self.julie)

        # Trying to add the role again using a Role with unique=True
        with self.assertRaises(InvalidRoleAssignment):
            assign_role(self.mike, Advisor, self.bob)

        # Trying to add the role again using a Role with unique=True
        with self.assertRaises(InvalidRoleAssignment):
            assign_role(self.mike, Advisor, self.julie)

        users_list = get_users(Advisor)
        self.assertEqual(users_list, [self.john])

    def test_unique_together(self):
        """ test if models marked as unique_together works fine """

        # Nothing attached to the object.
        users_list = self.unique.get_users()
        self.assertEqual(users_list, [])

        # Confirm that the object was attached to the user.
        self.mike.assign_role(UniqueOwner, self.unique)
        self.assertTrue(self.mike.has_role(UniqueOwner, self.unique))

        # Try to attach another role to the object
        # but using the same user instance.
        with self.assertRaises(InvalidRoleAssignment):
            self.mike.assign_role(Secretary, self.unique)

        # Remove the old role instance and try again
        # to attach the new role.
        self.mike.remove_role(UniqueOwner, self.unique)
        self.mike.assign_role(Secretary, self.unique)
        self.assertTrue(self.mike.has_role(Secretary, self.unique))

    def test_has_role(self):
        """ test if has_role method works fine """
        assign_role(self.john, Coordenator)
        assign_role(self.john, Advisor, self.bob)

        self.assertTrue(has_role(self.john, Coordenator))
        self.assertTrue(has_role(self.john, Advisor, self.bob))

        with self.assertRaises(NotAllowed):
            has_role(self.john, Advisor, self.unique)

    def test_has_permission(self):
        """ test if the has_permission method works fine """
        assign_role(self.john, Teacher, self.bob)
        self.assertTrue(has_permission(self.john, 'testapp1.add_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'testapp1.delete_user', self.bob))

        assign_role(self.mike, Secretary, self.bob)
        self.assertTrue(has_permission(self.mike, 'testapp1.delete_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'testapp1.add_user', self.bob))

        assign_role(self.bob, SubCoordenator)
        self.assertTrue(has_permission(self.bob, 'testapp1.change_user'))
        self.assertTrue(has_permission(self.bob, 'testapp1.change_user', self.julie))
        self.assertFalse(has_permission(self.bob, 'testapp1.add_user', self.julie))

        assign_role(self.julie, Coordenator)
        self.assertTrue(has_permission(self.julie, 'testapp1.add_user'))
        self.assertTrue(has_permission(self.julie, 'testapp1.add_user', self.bob))
        self.assertFalse(has_permission(self.julie, 'testapp1.change_user', self.bob))

    def test_template_tags(self):
        """ test if template tags work fine """
        assign_role(self.julie, Coordenator)

        self.assertTrue(tg_has_perm(self.julie, 'testapp1.add_user', self.bob))
        self.assertFalse(tg_has_perm(self.julie, 'testapp1.change_user', self.bob))

        # Check for non-object related role.
        self.assertEqual(tg_get_role(self.julie), 'Coordenator')

        # Check of object related role.
        assign_role(self.julie, Secretary, self.bob)
        self.assertEqual(tg_get_role(self.julie, self.bob), 'Secretary')

    def test_remove_roles(self):
        """ test if the remove_roles method works fine """
        assign_role(self.john, Teacher, self.bob)
        remove_role(self.john, Teacher, self.bob)

        users_list = get_users(Teacher)
        self.assertEqual(users_list, [])

        assign_roles([self.john, self.mike], Teacher, self.bob)
        remove_roles([self.john, self.mike], Teacher)

        users_list = get_users(Teacher)
        self.assertEqual(users_list, [])

        assign_role(self.julie, Coordenator)
        self.assertTrue(has_permission(self.julie, 'testapp1.add_user'))
        remove_role(self.julie)
        self.assertFalse(has_permission(self.julie, 'testapp1.add_user'))

    def test_assign_permissions(self):
        """ test if the permissions assignment works fine """

        # Assign the role and try to use a permission denied by default.
        assign_role(self.john, Teacher, self.bob)
        assign_role(self.john, Teacher, self.julie)
        self.assertFalse(has_permission(self.john, 'testapp1.delete_user', self.bob))
        self.assertFalse(has_permission(self.john, 'testapp1.delete_user', self.julie))

        # Explicitly assign the permission using access=True and the object.
        assign_permission(self.john, Teacher, 'testapp1.delete_user', True, self.bob)

        # Result: Only the specified object was affected.
        self.assertTrue(has_permission(self.john, 'testapp1.delete_user', self.bob))
        self.assertFalse(has_permission(self.john, 'testapp1.delete_user', self.julie))

        # Assign the role and try to use a permission allowed by default
        assign_role(self.mike, Teacher, self.bob)
        assign_role(self.mike, Teacher, self.julie)
        self.assertTrue(has_permission(self.mike, 'testapp1.add_user', self.bob))
        self.assertTrue(has_permission(self.mike, 'testapp1.add_user', self.julie))

        # Explicitly assign the permission using access=False but without an object.
        assign_permission(self.mike, Teacher, 'testapp1.add_user', False)

        # Result: All the user's role instances were affected
        self.assertFalse(has_permission(self.mike, 'testapp1.add_user', self.bob))
        self.assertFalse(has_permission(self.mike, 'testapp1.add_user', self.julie))

        # Trying to assign a wrong permission.
        with self.assertRaises(InvalidPermissionAssignment):
            assign_permission(self.mike, Secretary, 'testapp1.add_user', access=False)

        # Expliciting a permission to a role using ALL_MODELS.
        assign_role(self.julie, SubCoordenator)
        assign_permission(self.julie, SubCoordenator, 'testapp1.delete_user', access=True)
        self.assertTrue(has_permission(self.julie, 'testapp1.delete_user'))
