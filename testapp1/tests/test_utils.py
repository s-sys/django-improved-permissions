""" utils tests """
from django.test import TestCase

from improved_permissions.exceptions import ParentNotFound, RoleNotFound
from improved_permissions.utils import (get_model, get_parents, get_roleclass,
                                        string_to_permission)
from testapp1.models import MyUser


class FakeModel1(object):
    class RoleOptions:
        pass

class FakeModel2(object):
    class RoleOptions:
        permission_parents = ['hello']

class UtilsTest(TestCase):
    """ utils class tests """

    def test_exceptions(self):
        """ test all exceptions on utils module """
        with self.assertRaises(RoleNotFound):
            get_roleclass(12345)

        with self.assertRaises(RoleNotFound):
            get_roleclass('I am not a role.')

        self.assertEqual(get_model('I am not a model.'), None)

        self.assertEqual(get_parents(FakeModel1), [])
        
        with self.assertRaises(ParentNotFound):
            get_parents(FakeModel2)
