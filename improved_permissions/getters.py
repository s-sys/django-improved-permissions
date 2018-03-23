"""getters functions"""
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from improved_permissions.exceptions import NotAllowed
from improved_permissions.models import UserRole
from improved_permissions.utils import check_my_model, get_roleclass


def get_user(role_class=None, obj=None):
    """
    Get the User instance attached to the object.
    Only one UserRole must exists and this relation
    must be unique=True.

    Returns None if there is no user attached
    to the object.
    """
    query = UserRole.objects.select_related('user').all()
    role = None

    if role_class:
        # All users who have "role_class" attached to any object.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())

    if obj:
        # All users who have any role attached to the object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Looking for a role class using unique=True
    selected = list()
    for ur_obj in query:
        role = get_roleclass(ur_obj.role_class)
        if role.unique is True:
            selected.append(ur_obj.user)

    users_set = set(selected)
    if len(users_set) > 1:
        raise NotAllowed(
            'Multiple unique roles was found using '
            'the function get_user.  Use get_users '
            'instead.'
        )
    if len(users_set) == 1:
        return selected[0]
    return None


def get_users(role_class=None, obj=None):
    """
    If "role_class" and "obj" is provided,
    returns a QuerySet of users who has
    this role class attached to the
    object.

    If only "role_class" is provided, returns
    a QuerySet of users who has this role
    class attached to any object.

    If neither "role_class" or "obj" are provided,
    returns all users of the project.
    """

    query = get_user_model().objects.all()
    role = None

    if role_class:
        # All users who have "role_class" attached to any object.
        role = get_roleclass(role_class)
        query = query.filter(roles__role_class=role.get_class_name())

    if obj:
        # All users who have any role attached to the object.
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(roles__content_type=ct_obj.id, roles__object_id=obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, obj)

    # Return as a distinct QuerySet.
    return query.distinct()


def get_objects(user, role_class=None, model=None):
    """
    Return the list of objects attached
    to a given user.

    If "role_class" is provided, only the objects
    which as registered in that role class will
    be returned.

    If "model" is provided, only the objects
    of that model will be returned.
    """
    query = UserRole.objects.filter(user=user)
    role = None

    if role_class:
        # Filtering by role class.
        role = get_roleclass(role_class)
        query = query.filter(role_class=role.get_class_name())

    if model:
        # Filtering by model.
        ct_obj = ContentType.objects.get_for_model(model)
        query = query.filter(content_type=ct_obj.id)

    # Check if object belongs
    # to the role class.
    check_my_model(role, model)

    # TODO
    result = set(ur_obj.obj for ur_obj in query)
    # TODO
    return list(result)


def get_role(user, obj=None):
    """
    Proxy method to be used when you sure that
    will have only one role class attached.
    """
    return get_roles(user, obj)[0]


def get_roles(user, obj=None):
    """
    Return a list of role classes
    that is attached to "user".

    If "obj" is provided, the object
    must be attached as well.
    """
    query = UserRole.objects.filter(user=user)
    if obj:
        ct_obj = ContentType.objects.get_for_model(obj)
        query = query.filter(content_type=ct_obj.id, object_id=obj.id)

    # Transform the string representations
    # into role classes and return as list.
    return [get_roleclass(ur_obj.role_class) for ur_obj in query]
