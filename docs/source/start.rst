Quick Start
===========

The entire DIP permissions system works based on roles. In other words, if you want to have permissions between a user and a certain object, you need to define a role for this relationship.

Creating your first Role class
******************************

First, supose that you have the following model in your ``models.py``: ::

    # myapp/models.py

    from django.db import models

    class Book(models.Model):
        title = models.CharField(max_length=256)
        content = models.TextField(max_length=1000)

        class Meta:
            permissions = (
                ('read_book', 'Can Read Book'),
                ('review_book', 'Can Review Book')
            )

.. note:: Notice that the permission statements inside models is exactly like the Django ``auth`` system.

Now, create a new file inside of any app of your project named ``roles.py`` and implement as follows: ::

    # myapp/roles.py

    from improved_permissions.roles import Role
    from myapp.models import Book

    class Author(Role):
        verbose_name = "Author"
        models = [Book]
        deny = ['myapp.review_book']

    class Reviewer(Role):
        verbose_name = "Reviewer"
        models = [Book]
        allow = ['myapp.review_book']

Ready! You can now use the DIP functions to assign, remove, and check permissions.

Every time your project starts, we use an ``autodiscover`` in order to validate and register your Role classes automatically. So, don't worry about to do anything else.

Using the first shortcuts
*************************

Once you implement the role classes, you are ready to use our shortcuts. For example, let's create a ``Book`` object and an ``Author`` role for a user: ::

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission, has_role
    
    from myapp.models import Book
    from myapp.roles import Author, Reviewer


    john = User.objects.get(pk=1)
    book = Book.objects.create(title='Nice Book', content='Such content.')

    has_role(john, Author, book)
    >>> False
    has_permission(john, 'myapp.read_book', book)
    >>> False

    assign_role(john, Author, book)

    has_role(john, Author, book)
    >>> True
    has_permission(john, 'myapp.read_book', book)
    >>> True
    has_permission(john, 'myapp.review_book', book)
    >>> False

You just met the shortcuts ``assign_role``, ``has_role`` and ``has_permission``. If you don't get how they work, no problem. First, let's understand all about implementing ``Role`` classes in the next section.
