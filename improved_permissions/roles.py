"""definition of role"""
import inspect

from django.apps import apps
from django.db.models import Model as DJANGO_MODEL

from improved_permissions.exceptions import ImproperlyConfigured

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
        raise ImproperlyConfigured('Role classes must not be instantiated.')

    """
    PARENT ROLE ONLY HELPER METHODS
    """

    @classmethod
    def parent(cls):
        if cls != Role:
            raise ImproperlyConfigured('Only the Role class is all'
                                       'owed to call this method.')

    @classmethod
    def register_role(cls, new_class):
        cls.parent()
        if new_class in cls._ROLE_CLASSES_LIST:
            raise ImproperlyConfigured('"{}" class was already registered a valid '
                                       'Role class.'.format(new_class.get_class_name()))
        new_class.validate()
        cls._ROLE_CLASSES_LIST += new_class

    @classmethod
    def get_roles(cls):
        cls.parent()
        return list(cls._ROLE_CLASSES_LIST)


    """
    ALL ROLE CLASSES HELPER METHODS
    """

    @classmethod
    def validate(cls):
        """
        Check if all attributes needed
        was properly defined.
        """

        # Check for "verbose_name" declaration.
        if not hasattr(cls, 'verbose_name'):
            raise ImproperlyConfigured('Provide a "verbose_name" declaration to '
                                       'the Role class "{}".'.format(cls.__name__))

        # Check if "models" is a valid list of Django models.
        if hasattr(cls, 'models') and isinstance(cls.models, list):
            check = True
            for model in cls.models:
                if not inspect.isclass(model) or not issubclass(model, DJANGO_MODEL):
                    check = False
                    break
            if check:
                return
        raise ImproperlyConfigured('Provide a list of Models classes via '
                                   'declaration of "models" to the Role '
                                   'class "{}".'.format(cls.__name__))

    @classmethod
    def get_class_name(cls):
        return str(cls.__name__.lower())

    @classmethod
    def get_verbose_name(cls):
        return str(cls.verbose_name)

    @classmethod
    def get_models(cls):
        ref = list()
        if isinstance(cls.models, list):
            ref = list(cls.models)
        elif cls.models == ALL_MODELS:
            ref = list(apps.get_models())  # All models known by Django.
        return ref

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
    exclude = []
