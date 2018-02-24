"""definition of role"""
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase


ALL_MODELS = -1


class Role(object):
    """
    Role

    This abstract class is used
    to manage all requests regarding
    role permissions.

    """

    def __new__(cls, *args, **kwargs):
        raise AssertionError("Role classes must not be instantiated.")

    @classmethod
    def get_verbose_name(cls):
        if hasattr(cls, 'verbose_name'):
            return str(cls.verbose_name)
        raise ImproperlyConfigured('Provide a "verbose_name" to the '
                                   'role class "{}".'.format(cls.__name__))

    @classmethod
    def get_models(cls):
        if hasattr(cls, 'model') != hasattr(cls, 'models'):
            if hasattr(cls, 'model') and type(cls.model) == ModelBase:
                return [cls.model]
            elif isinstance(cls.models, list):
                models_list = list()
                for model in cls.models:
                    if type(model) == ModelBase:
                        models_list.append(model)
                if cls.models == models_list:
                    return cls.models

        raise ImproperlyConfigured('Provide either a Model class via "model"' 
                                   'or list of Model classes via "models".')


class SuperUserRole(Role):
    """
    Super User Role
    """
    verbose_name = 'Super User Role'
    models = ALL_MODELS
    inherit = True
