""" RoleManager tests """
from django.apps import apps
from django.test import TestCase

from improved_permissions.exceptions import ImproperlyConfigured, NotAllowed
from improved_permissions.roles import ALL_MODELS, Role, RoleManager
from testapp1 import roles


class Advisor(Role):
    verbose_name = "Advisor"
    models = ALL_MODELS
    unique = True
    deny = []


class RoleTest(TestCase):
    """ Role class tests """

    def setUp(self):
        RoleManager.cleanup()
        RoleManager.register_role(roles.Advisor)
        RoleManager.register_role(roles.Coordenator)

    def test_incorrect_implementations(self):
        """ test for exceptions """

        # Trying to instantiate.
        with self.assertRaises(ImproperlyConfigured):
            Role()

        # Trying to use the methods on the abstract class.
        with self.assertRaises(ImproperlyConfigured):
            Role.get_class_name()

        # Trying to register another class but using
        # the same name.
        with self.assertRaises(ImproperlyConfigured):
            RoleManager.register_role(Advisor)

        # Trying to access the inherit mode of a 
        # role class using inherit=False.
        with self.assertRaises(NotAllowed):
            roles.Advisor.get_inherit_mode()

        # Check if the role class using ALL_MODELS
        # actually get all models by your method.
        models_list = roles.Coordenator.get_models()
        self.assertEqual(models_list, apps.get_models())
