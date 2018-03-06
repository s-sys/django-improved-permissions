Roles
==============

The Roles' File
^^^^^^^^^^^^^^^

oi ``myapp/roles.py``: ::

	from improved_permissions.roles import Role

	class TeacherRole(Role):
		verbose_name = "Teacher"
		models = [User]
		deny = []

Required attributes
^^^^^^^^^^^^^^^^^^^

The required attributes in the role classes are:

``verbose_name``: String representation of the role.

``models``: List of models allowed to be attached to this role.

``allow`` or ``deny``: List of valid permissions.

Optional Attributes
^^^^^^^^^^^^^^^^^^^

``unique``: Bool value.

``inherit``: Bool value.

``inherit_allow`` or ``inherit_deny``: List of valid permissions.
