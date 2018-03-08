Shortcuts
=========

These functions are the heart of this app. Everything you need to do in your project is implemented in the ``shortcuts`` module.

.. note:: Do not rush your project using the shortcuts directly. We have an easiest way to use these shorcuts using **mixins** in your models. Click here to check it out. 


Checkers
^^^^^^^^

.. function:: has_role(user, role_class, obj=None)

Returns True if the user has the role to the object.

.. function:: has_permission(user, permission, obj=None)

Returns True if the user has the permission.

Assigning and Revoking
^^^^^^^^^^^^^^^^^^^^^^

.. function:: assign_role(user, role_class, obj=None)

Assign the role to the user.

.. function:: assign_roles(users_list, role_class, obj=None)

Assign the role to all users in the list.

.. function:: remove_role(user, role_class, obj=None)

Remove the role and your permissions of the object from the user. 

.. function:: remove_roles(users_list=None, role_class, obj=None)

Remove the role and your permissions of the object from all users in the list.


Getters
^^^^^^^

.. function:: get_role(user, obj=None)

Get the unique role class of the user related to the object.

.. function:: get_roles(user, obj=None)

Get all role classes of the user related to the object.

.. function:: get_user(role_class=None, obj=None)

Get the unique user instance according to the object.

.. function:: get_user(role_class=None, obj=None)

Get the unique user instance according to the object.

.. function:: get_users(role_class=None, obj=None)

Get all users instances according to the object.

.. function:: get_objects(user, role_class=None, model=None)

Get all objects related to the user.
