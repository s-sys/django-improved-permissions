Quick Start
===========


Creating your first Role Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, supose that you have the following model in your ``models.py``: ::

    from django.db import models

    class Book(models.Model):
        title = models.CharField(max_length=256)
        content = models.TextField(max_length=1000)

        class Meta:
            permissions = (
                ('read_book', 'Can Read Book'),
                ('review_book', 'Can Review Book')
            )

Now, create a new file inside of any app of your project named ``roles.py`` and implement as follows: ::

    from improved_permissions.roles import Role
    from myapp.models import Book

    class Author(Role):
        verbose_name = "Author"
        models = [Book]
        deny = ['myapp.review']

    class Reviewer(Role):
        verbose_name = "Reviewer"
        models = [Book]
        allow = ['myapp.review']

Every time your project starts, we use an ``autodiscover`` in order to validade and register your role classes automatically. So, don't worry to do anything else.

Using the shortcuts
^^^^^^^^^^^^^^^^^^^

Once you implement the role classes, you are ready to use our shortcuts functions in ``improved_permissions.shortcuts``. For instance: ::

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission
    
    from myapp.models import Book
    from myapp.roles import Author, Reviewer


    john = User.objects.get(pk=1)
    book = Book.objects.get(pk=1)

    has_permission(john, 'myapp.read_book', book)
    >>> False
    assign_role(john, Author, book)
    has_permission(john, 'myapp.read_book', book)
    >>> True
