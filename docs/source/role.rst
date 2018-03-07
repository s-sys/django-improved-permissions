Role Class
==============

File Structure
^^^^^^^^^^^^^^

oi ``myapp/roles.py``: ::

	from improved_permissions.roles import Role

	class TeacherRole(Role):
		verbose_name = "Teacher"
		models = [User]
		deny = []

Required attributes
^^^^^^^^^^^^^^^^^^^

The ``Role`` class has some attributes that are required to be properly registered by our ``RoleManager``. The description of these attributes is in the following table:

===================== ========================== ===
Attribute             Type                       Description
===================== ========================== ===
``verbose_name``      ``string``                 Used to print some information about the role.
``models``            ``list`` or ``ALL_MODELS`` Defines which models this role can be attached.
``allow`` or ``deny`` ``list``                   Defines which permissions should be allowed or denied. You must define only one of them.
===================== ========================== ===

Optional Attributes
^^^^^^^^^^^^^^^^^^^

The ``Role`` class also has other attributes, which are considered as optional. When they are not declared, we assign default values for these arguments.

===================================== ======== ========= ===
Attribute                             Type     Default   Description
===================================== ======== ========= ===
``unique``                            ``bool`` ``False`` Only one User instance is allowed to be attached to a given object using this role.
``inherit``                           ``bool`` ``False`` Allows this role to inherit permissions from its child models. Read about this feature here.
``inherit_allow`` or ``inherit_deny`` ``list`` ``[]``    Specifies which inherit permissions should be allowed or denied. You must define only one of them.
===================================== ======== ========= ===

Public Methods
^^^^^^^^^^^^^^

We also have some methods.

.. function:: get_verbose_name(): string

Returns the ``verbose_name`` attribute.

.. function:: is_my_model(model): bool

Checks if the role can be attached to the argument ``model``. The argument can be either the model class or an instance.

.. function:: get_models(): list

Returns a list of all model classes which this role can be attached. If the ``models`` attribute was defined using ``ALL_MODELS``, this method will return a list of all valid models of the project.
