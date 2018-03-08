Permissions Inheritance
=======================

hil

Class RoleOptions
^^^^^^^^^^^^^^^^^
The class ``RoleOptions`` works just like the ``Meta`` class in the Django models, helping us to define some attributes related to that model.

Let's go back to that first example, the model ``Book``. We are going to implement another model named ``Library`` and create a ``ForeignKey`` field in ``Book`` to create a relationship between them. So, our ``models.py`` will be something like that: ::

    # myapp/models.py

    from django.db import models

    class Library(models.Model):
        name = models.CharField(max_length=256)


    class Book(models.Model):
        title = models.CharField(max_length=256)
        content = models.TextField(max_length=1000)
        my_library = models.ForeignKey(Library)

        class Meta:
            permissions = (
                ('read_book', 'Can Read Book'),
                ('review_book', 'Can Review Book')
            )

We need to say to DIP that the ``my_library`` represents a parent of the ``Book`` model. In other words, any roles related to the ``Library`` model with ``inherit=True`` will be elected to search for more permissions.

The way to do this is implementing another inner class in the model, the class ``RoleOptions``: ::

    # myapp/models.py

    from django.db import models
    from improved_permissions.mixins import RoleMixin


    class Library(models.Model, RoleMixin):
        name = models.CharField(max_length=256)


    class Book(models.Model, RoleMixin):
        title = models.CharField(max_length=256)
        content = models.TextField(max_length=1000)
        my_library = models.ForeignKey(Library)

        class Meta:
            permissions = (
                ('read_book', 'Can Read Book'),
                ('review_book', 'Can Review Book')
            )

        class RoleOptions:
            permission_parents = ['my_library']

Now, to the terminal to make some tests: ::

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission
    from myapp.models import Book, Library


    john = User.objects.get(pk=1)

    library = Library.objects.create(name='Important Library')
    book = Book.objects.create(title='New Book', content='Much content', my_library=library)

    # John has nothing :(
    has_permission(john, 'myapp.read_book', book)
    >>> False

    # John receives an role attached to "library".
    assign_role(john, LibraryManager, library)

    # Now, we got True by permission inheritance.
    has_permission('myapp.read_book', book)
    >>> True

The class ``RoleOptions`` has the following attributes:

====================== ======== ===========
Attribute              Type     Description
====================== ======== ===========
``permission_parents`` ``list`` List of ``ForeignKey`` or ``GenericForeignKey`` fields on the model to be considered as *parent* of the model.
``unique_together``    ``bool`` If ``True``, this model only allows one assignment to any User instance.
====================== ======== ===========

Inheritance Settings
^^^^^^^^^^^^^^^^^^^^

oi
