""" permissions utils """
import inspect

from improved_permissions import exceptions


def is_role(role_class):
    """
    Check if the argument is a valid Role class.
    This method DOES NOT check if the class is registered in RoleManager.
    """
    from improved_permissions.roles import Role
    return inspect.isclass(role_class) and issubclass(role_class, Role) and role_class != Role


def get_roleclass(role_class):
    """
    Get the role class signature
    by string or by itself.
    """
    from improved_permissions.roles import RoleManager
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


def get_permissions_list(model_instance, inherit=False):
    """
    Get the list of permissions explicit
    declared in the class Permissions.
    """
    perms_list = list()
    models_stack = list()
    models_stack.append(model_instance)

    # -----
    # Start the Breath-First Search for permissions.
    # https://en.wikipedia.org/wiki/Breadth-first_search
    # -----
    while models_stack:
        model = models_stack.pop(0) # pop head of the stack.
        
        if hasattr(model, 'Permissions'):
            perm_class = model.Permissions

            # Search for permissions and
            # append the items in "perms_list".
            if hasattr(perm_class, 'permissions'):
                perms_list += perm_class.permissions

            # If inherit = False, the BFS
            # actually perform only one loop.
            if not inherit:
                break

            # Now, we verify if any field of the model
            # was marked as "parent" in order to inherit
            # their permissions.
            if hasattr(perm_class, 'permission_parents'):
                parents_list = perm_class.permission_parents
                for parent in parents_list:
                    if hasattr(model, parent):
                        models_stack.append(getattr(model, parent))
                    else:
                        raise exceptions.ParentNotFound()
    return perms_list
