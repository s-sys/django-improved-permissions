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

2. create a module in your app called roles.py e write the following::

	from improved_permissions import Role

	class Friend(Role):
		verbose_name = "Friend"
		models = [Book]
		deny = []

3. In your model, write the permissions normally::

	from django.db import models

	class Book(models.Model):
		title = models.CharField(max_length=256)

4. Now, use our shortcuts methods to assign or remove a role to a user::

	from improved_permissions.shortcuts import assign_role
	from myapp.models import Book

		user = User.objects.get(username='root')
		book = Book.objects.get(pk=1)
		assign_role(user, Friend, book)

5. Ready!
