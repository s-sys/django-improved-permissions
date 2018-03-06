""" definition of role and rolemanager """
from django.apps import apps

from improved_permissions.exceptions import ImproperlyConfigured, NotAllowed
from improved_permissions.utils import get_model, string_to_permission

ALLOW_MODE = 0
DENY_MODE = 1

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

        # Check if is actually a role class.
        if not is_role(new_class):
            raise ImproperlyConfigured(
                '"%s" is not a class inherited '
                'from Role.' % str(new_class)
            )

        # Looking for name conflits or if this
        # class was already registered before.
        new_name = new_class.get_class_name()
        for current_class in cls.__ROLE_CLASSES_LIST:
            current_name = current_class.get_class_name()
            if current_class == new_class:
                raise ImproperlyConfigured(
                    '"%s" was already registered as '
                    'a valid Role class.' % new_name
                )

            elif current_name == new_name:
                raise ImproperlyConfigured(
                    '"Another role was already defined using '
                    '"%s". Choose another name for this Role '
                    'class.' % current_name
                )

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
    def __validate(cls, new_class):  # pylint: disable=too-many-branches
        """
        Check if all attributes needed
        was properly defined in the
        new Role class.
        """
        name = new_class.get_class_name()

        # Check for "verbose_name" definition.
        if not hasattr(new_class, 'verbose_name'):
            raise ImproperlyConfigured(
                'Provide a "verbose_name" definition '
                'to the Role class "%s".' % name
            )

        # Check if the atribute "models" is
        # defined correctly.
        cls.__validate_models(new_class)

        # Role classes with "models" = ALLMODELS
        # does not use allow/deny. In this case,
        # all permissions must be specified in
        # "inherit_allow" and "inherit_deny".
        if new_class.models != ALL_MODELS:
            new_class.MODE = cls.__validate_allow_deny(new_class, 'allow', 'deny')

        # Ensuring that "inherit" exists.
        # Default: False
        if not hasattr(new_class, 'inherit') or not isinstance(new_class.inherit, bool):
            new_class.inherit = False

        if new_class.inherit is True:
            new_class.INHERIT_MODE = cls.__validate_allow_deny(new_class, 'inherit_allow', 'inherit_deny')

        # Ensuring that "unique" exists.
        # Default: False
        if not hasattr(new_class, 'unique') or not isinstance(new_class.unique, bool):
            new_class.unique = False

    @classmethod
    def __validate_models(cls, new_class):
        """
        Check if the attribute "models" is a valid list
        of Django models or the constant ALL_MODELS.
        """
        name = new_class.get_verbose_name()

        models_isvalid = True
        if hasattr(new_class, 'models'):
            if isinstance(new_class.models, list):
                # Check for every item in the "models" list.
                valid_list = list()
                for model in new_class.models:
                    # Get the model class or "app_label.model".
                    model_class = get_model(model)
                    if model_class:
                        valid_list.append(model_class)
                    else:
                        models_isvalid = False
                        break
                new_class.models = valid_list
            elif new_class.models == ALL_MODELS:
                # Role classes with ALL_MODELS autoimplies inherit=True.
                new_class.inherit = True
                new_class.unique = False
                new_class.MODE = DENY_MODE
                new_class.allow = []
                new_class.deny = []
            else:
                models_isvalid = False
        else:
            models_isvalid = False

        if not models_isvalid:
            raise ImproperlyConfigured(
                'Provide a list of Models classes via definition '
                'of "models" to the Role class "%s".' % name
            )

    @classmethod
    def __validate_allow_deny(cls, new_class, allow_field, deny_field):
        """
        This method validates the set attributes "allow/inherit_allow"
        and "deny/inherit_deny", checking if their values are a valid
        list of permissions in string representation.
        """
        name = new_class.get_verbose_name()

        # Checking for "allow" and "deny" fields
        c_allow = hasattr(new_class, allow_field)
        c_deny = hasattr(new_class, deny_field)

        # XOR operation.
        if c_allow and c_deny or not c_allow and not c_deny:
            raise ImproperlyConfigured(
                'Provide either "%s" or "%s" when inherit=True'
                ' or models=ALL_MODELS for the Role "%s".'
                '' % (allow_field, deny_field, name)
            )

        if c_allow and isinstance(getattr(new_class, allow_field), list):
            perms_list = getattr(new_class, allow_field)
            result = ALLOW_MODE

        elif c_deny and isinstance(getattr(new_class, deny_field), list):
            perms_list = getattr(new_class, deny_field)
            result = DENY_MODE
        else:
            raise ImproperlyConfigured(
                '"%s" or "%s" must to be a list in the Role '
                '"%s".' % (allow_field, deny_field, name)
            )

        # Check if the permissions given via "inherit_allow"
        # or "inherit_deny" exists in the Permission database.
        from django.contrib.auth.models import Permission
        for perm in perms_list:
            try:
                string_to_permission(perm)
            except (AttributeError, Permission.DoesNotExist):
                raise ImproperlyConfigured(
                    '"%s" does not exist in the Permission database.' % perm
                )
        # Return the mode.
        return result


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
    def get_mode(cls):
        cls.__protect()
        return cls.MODE

    @classmethod
    def get_inherit_mode(cls):
        cls.__protect()
        if cls.inherit is True:
            return cls.INHERIT_MODE
        raise NotAllowed(
            'The role "%s" is not marked as unique.' % cls.get_verbose_name()
        )

    @classmethod
    def get_models(cls):
        cls.__protect()
        if cls.models == ALL_MODELS:
            return list(apps.get_models())  # All models known by Django.
        return list(cls.models)

    @classmethod
    def is_my_model(cls, model):
        cls.__protect()
        return model._meta.model in cls.get_models()  # pylint: disable=protected-access
