""" utils tests """
from django.test import TestCase

from improved_permissions.exceptions import (ImproperlyConfigured,
                                             ParentNotFound, RoleNotFound)
from improved_permissions.utils import (autodiscover, get_model, get_parents,
                                        get_roleclass, is_unique_together,
                                        string_to_permission)
from testapp1.models import MyUser


class FakeModel1(object):
    class RoleOptions:
        pass


class FakeModel2(object):
    class RoleOptions:
        permission_parents = ['hello']


class FakeModel3(object):
    class RoleOptions:
        unique_together = 'not a bool value'


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

        with self.assertRaises(ImproperlyConfigured):
            is_unique_together(FakeModel3)
