""" models tests """
from django.core.exceptions import ValidationError
from django.test import TestCase

from improved_permissions.models import UserRole
from improved_permissions.roles import Role, RoleManager
from testapp1.models import MyUser
from testapp1.roles import Advisor, Coordenator


class ModelsTest(TestCase):
    """ test methods in the model module """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Coordenator)

        self.john = MyUser.objects.create(username='john')
        self.bob = MyUser.objects.create(username='bob')

    def test_output(self):
        """ check if the str method works fine """
        self.john.assign_role(Advisor, self.bob)
        obj = UserRole.objects.get(user=self.john)
        self.assertEqual(str(obj), 'john is Advisor of bob')

        self.bob.assign_role(Coordenator)
        obj = UserRole.objects.get(user=self.bob)
        self.assertEqual(str(obj), 'bob is Coordenator')

    def test_edit_incorrectly(self):
        """
        check if its possible to put 
        wrong role class into UserRole
        """
        self.john.assign_role(Advisor, self.bob)

        with self.assertRaises(ValidationError):
            obj = UserRole.objects.get(user=self.john)
            obj.role_class = 'this class doesnt exist.'
            obj.save()
