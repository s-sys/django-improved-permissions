=====
Django Improved Permissions
=====

TODO

Quick start
-----------

1. pip install django-improved-permissions

2. Add "improved_permissions" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'improved_permissions',
    ]


3. You can already use the DIP!

Creating your first Role
------------------------

1. First of all, if you want a relationship between an User and a Django Model, you must to create a Role in order to represent this relation.

2. Create a module in your app called roles.py and write the following::

	from improved_permissions.roles import Role

	class Friend(Role):
		verbose_name = "Friend"
		models = [Book]
		deny = []

3. Every time your Django project starts, we run a simple autodiscover in order to auto register your role classes. So, don't worry to do anything else.

4. In your model, write the permissions normally::

	from django.db import models

	class Book(models.Model):
		title = models.CharField(max_length=256)
		content = models.TextField(max_length=1000)

		class Meta:
			permissions = [('review', 'Review Book'),]

5. Now, use our shortcuts methods to assign or remove a role to a user::

	from improved_permissions.shortcuts import assign_role
	from myapp.roles import Friend
	from myapp.models import Book

		user = User.objects.get(username='root')
		book = Book.objects.get(pk=1)
		assign_role(user, Friend, book)

		has_permission(user, 'myapp.review', book)
		>>> True

Improving your Role class
-------------------------

1. TODO

Applying the concept of "parents"
---------------------------------

1. TODO

Mixins
------

1. RoleMixin

2. UserRoleMixin

3. PermissionMixin
