"""definition of role"""
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

ALL_MODELS = -1


class Role(object):
    """
    Role

    This abstract class is used
    to manage all requests regarding
    role permissions.

    """

    _ROLE_CLASSES_LIST = list()

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        raise AssertionError("Role classes must not be instantiated.")

    @classmethod
    def get_class_name(cls):
        return str(cls.__name__.lower())

    @classmethod
    def get_verbose_name(cls):
        if hasattr(cls, 'verbose_name'):
            return str(cls.verbose_name)
        raise ImproperlyConfigured('Provide a "verbose_name" to the '
                                   'role class "{}".'.format(cls.__name__))

    @classmethod
    def get_roles(cls):
        return list(cls._ROLE_CLASSES_LIST)

    @classmethod
    def get_models(cls):
        if isinstance(cls.models, list):
            models_list = list()
            for model in cls.models:
                if issubclass(model, models.Model):
                    models_list.append(model)
            if cls.models == models_list:
                return cls.models
        elif cls.models == ALL_MODELS:
            return apps.get_models()  # all models known by Django

        raise ImproperlyConfigured('Provide a list of Model classes via "models".')

    @classmethod
    def is_my_model(cls, model):
        return model in cls.get_models()


class SuperUser(Role):
    """
    Super User Role
    """
    verbose_name = 'Super User Role'
    models = ALL_MODELS
    inherit = True
