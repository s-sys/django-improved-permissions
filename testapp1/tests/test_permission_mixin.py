""" permission mixin tests """
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.test import TestCase

from improved_permissions.mixins import PermissionMixin
from improved_permissions.roles import RoleManager
from testapp1.models import MyUser
from testapp1.roles import Advisor


class Request(object):
    user = None


class Dispatch(object):
    def dispatch(self, request, *args, **kwargs):
        return 'Protected View'


class RequestView(PermissionMixin, Dispatch):
    def __init__(self, user=None, string=None, obj=None):
        if user:
            self.request = Request()
            self.request.user = user
        if string:
            self.permission_string = string
        if obj:
            self.permission_object = obj


class ObjectView(PermissionMixin):
    def __init__(self, obj):
        self.my_object = obj

    def get_object(self):
        return self.my_object


class PermissionMixinTest(TestCase):
    """ test if the permissionmixin works fine """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(Advisor)

        self.john = MyUser.objects.create(username='john')
        self.bob = MyUser.objects.create(username='bob')

    def test_set_string(self):
        """ ... """
        view = RequestView(string='Hello!')
        perm_string = view.get_permission_string()
        self.assertEqual(perm_string, 'Hello!')

        with self.assertRaises(ImproperlyConfigured):
            view.get_permission_object()

        view.permission_object = self.bob
        perm_obj = view.get_permission_object()
        self.assertEqual(perm_obj, self.bob)

    def test_set_object(self):
        """ ... """
        view = RequestView(obj=self.john)
        perm_obj = view.get_permission_object()
        self.assertEqual(perm_obj, self.john)

        with self.assertRaises(ImproperlyConfigured):
            view.get_permission_string()

        view.permission_string = 'Hello!'
        perm_string = view.get_permission_string()
        self.assertEqual(perm_string, 'Hello!')

        view = ObjectView(self.john)
        perm_obj = view.get_permission_object()
        self.assertEqual(perm_obj, self.john)

    def test_despatch(self):
        """ ... """
        self.bob.assign_role(Advisor, self.john)
        view = RequestView(user=self.bob, obj=self.john)
        view.permission_string = 'testapp1.add_user'
        self.assertEqual(view.dispatch(None), 'Protected View')

        view.permission_string = 'testapp1.review'
        with self.assertRaises(PermissionDenied):
            view.dispatch(None)
