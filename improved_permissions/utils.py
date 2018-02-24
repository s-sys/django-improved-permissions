""" permissions utils """
import inspect

from improved_permissions import exceptions
from improved_permissions.roles import Role, RoleManager


def is_role(role_class):
    """
    Check if the argument is a valid Role class.
    This method DOES NOT check if the class is registered in RoleManager.
    """
    return inspect.isclass(role_class) and issubclass(role_class, Role) and role_class != Role


def get_roleclass(role_class):
    """
    Get the role class signature
    by string or by itself.
    """
    roles_list = RoleManager.get_roles()
    if role_class in roles_list:
        # Already a Role class.
        return role_class

    elif isinstance(role_class, str):
        # Trying to get via string.
        for role in roles_list:
            if role.get_class_name() == role_class:
                return role

    raise exceptions.RoleNotFound()


def get_permissions_list(model_instance):
    """
    Get the list of permissions explicit
    declared in the class Permissions.

    Example:
    --
    class Project(models.Model):
        title = models.CharField(max_length=256)
        my_program = models.ForeignKey(Program)

        class Meta:
            verbose_name = "Project"

        class Permissions:
            permissions = ('view_project',)
    --

    Result (strings): ['view_project']
    """
    if hasattr(model_instance, 'Permissions'):
        perm_class = model_instance.Permissions
        if hasattr(perm_class, 'permissions'):
            return perm_class.permissions
    raise exceptions.ModelNotDefined()


def get_permissions_parents(model_instance):
    """
    Get the list of objects declared as 'parents'
    of a given Model instance.

    In other words, these fields' models inherit
    all permissions declared in this Model class.

    Example:
    --
    class Program(models.Model):
        title = models.CharField(max_length=256)

    class Project(models.Model):
        title = models.CharField(max_length=256)
        my_program = models.ForeignKey(Program)

        class Meta:
            verbose_name = "Project"

        class Permissions:
            permissions = ('view_project',)
            permission_parents = ['my_program']
    --

    Result (instances): [my_program]
    """
    if hasattr(model_instance, 'Permissions'):
        perm_class = model_instance.Permissions
        if hasattr(perm_class, 'permission_parents'):
            objects = list()
            parents_list = perm_class.permission_parents
            for parent in parents_list:
                if hasattr(model_instance, parent):
                    objects.append(getattr(model_instance, parent))
                else:
                    raise exceptions.ParentNotFound()
            return objects
    raise exceptions.ModelNotDefined()
