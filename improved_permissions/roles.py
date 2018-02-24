"""definition of role and rolemanager """
import inspect

from django.apps import apps
from django.db.models import Model as DJANGO_MODEL

from improved_permissions.exceptions import ImproperlyConfigured

ALL_MODELS = -1


class RoleManager(object):
    """
    RoleManager

    This class holds the list
    of all Role classes validated
    and in use by the project.

    """
    __ROLE_CLASSES_LIST = list()

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        raise ImproperlyConfigured('RoleManager must not be instantiated.')

    @classmethod
    def register_role(cls, new_class):
        """
        Validate and register a new Role
        class in the Manager to be used
        in the project.
        """
        from improved_permissions.utils import is_role
        if not is_role(new_class):
            raise ImproperlyConfigured('"{object}" is not a class inherited '
                                       'from Role.'.format(object=str(new_class)))

        if new_class in cls.__ROLE_CLASSES_LIST:
            name = new_class.get_class_name()
            raise ImproperlyConfigured('"{name}" class was already registered '
                                       'a valid Role class.'.format(name=name))
        cls.__validate(new_class)
        cls.__ROLE_CLASSES_LIST.append(new_class)

    @classmethod
    def get_roles(cls):
        """
        Return the list of
        all registered Role
        classes.
        """
        return list(cls.__ROLE_CLASSES_LIST)

    @classmethod
    def cleanup(cls):
        """
        Flush the current list of all
        Roles registered in the project.
        """
        cls.__ROLE_CLASSES_LIST = list()

    @classmethod
    def __validate(cls, new_class):
        """
        Check if all attributes needed
        was properly defined in the
        new Role class.
        """

        name = new_class.get_class_name()

        # Check for "verbose_name" declaration.
        if not hasattr(new_class, 'verbose_name'):
            raise ImproperlyConfigured('Provide a "verbose_name" declaration to the '
                                       'Role class "{name}".'.format(name=name))

        # Check if "models" is a valid list of Django models or ALL_MODELS.
        models_isvalid = True
        if hasattr(new_class, 'models'):
            if isinstance(new_class.models, list):
                for model in new_class.models:
                    if not inspect.isclass(model) or not issubclass(model, DJANGO_MODEL):
                        models_isvalid = False
                        break
            elif new_class.models != ALL_MODELS:
                models_isvalid = False
        else:
            models_isvalid = False

        if not models_isvalid:
            raise ImproperlyConfigured('Provide a list of Models classes via '
                                       'declaration of "models" to the Role '
                                       'class "{name}".'.format(name=name))

        # Ensuring that "unique" exists.
        if not hasattr(new_class, 'unique') or not isinstance(new_class.unique, bool):
            new_class.unique = False


class Role(object):
    """
    Role

    This abstract class is used
    to manage all requests regarding
    role permissions.

    """

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        raise ImproperlyConfigured('Role classes must not be instantiated.')

    @classmethod
    def __protect(cls):
        if cls == Role:
            raise ImproperlyConfigured('The role class itself must not be used.')

    @classmethod
    def get_class_name(cls):
        cls.__protect()
        return str(cls.__name__.lower())

    @classmethod
    def get_verbose_name(cls):
        cls.__protect()
        return str(cls.verbose_name)

    @classmethod
    def get_models(cls):
        cls.__protect()
        ref = list()
        if isinstance(cls.models, list):
            ref = list(cls.models)
        elif cls.models == ALL_MODELS:
            ref = list(apps.get_models())  # All models known by Django.
        return ref

    @classmethod
    def is_my_model(cls, model):
        cls.__protect()
        if not isinstance(model, DJANGO_MODEL):
            raise ImproperlyConfigured('The argument is not a Django model.')
        return model._meta.model in cls.get_models()


class SuperUser(Role):
    """
    Super User Role
    """
    verbose_name = 'Super User Role'
    models = ALL_MODELS
    inherit = True
    exclude = []
