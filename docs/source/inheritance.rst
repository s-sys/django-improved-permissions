Permissions Inheritance
=======================

The DIP allows you to implement inheritance permissions for your objects. For example, a librarian does't need to have explicit permissions to all their books in his library as long as the books make it clear that the library is an object in which it "belongs" to.

Class RoleOptions
^^^^^^^^^^^^^^^^^

The class ``RoleOptions`` works just like the ``Meta`` class in the Django models, helping us to define some attributes related to that specific model. This class has the following attributes:

====================== =================== ===========
Attribute              Type                Description
====================== =================== ===========
``permission_parents`` ``list`` of ``str`` List of ``ForeignKey`` or ``GenericForeignKey`` fields on the model to be considered as *parent* of the model.
``unique_together``    ``bool``            If ``True``, this model only allows one assignment to any User instance.
====================== =================== ===========

Working with the inheritance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

The way to do this is implementing another inner class in the model, the class ``RoleOptions`` and defining the list ``permission_parents``: ::


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

Let's create a new role in order to represent the ``Library`` instances. ::


    # myapp/roles.py

    from improved_permissions.roles import Role
    from myapp.models import Library

    class LibraryManager(Role):
        verbose_name = 'Library Manager'
        models = [Library]
        allow = []
        inherit = True
        inherit_allow = ['myapp.read_book']

After that, the field ``my_library`` already represents a parent model of the ``Book``. Now, let's go to the terminal to make some tests: ::

    # Django Shell

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission
    from myapp.models import Book, Library
    from myapp.roles import LibraryManager

    john = User.objects.get(pk=1)

    library = Library.objects.create(name='Important Library')
    book = Book.objects.create(title='New Book', content='Much content', my_library=library)

    # John has nothing :(
    has_permission(john, 'myapp.read_book', book)
    >>> False

    # John receives an role attached to "library".
    assign_role(john, LibraryManager, library)

    # Now, we got True by permission inheritance.
    has_permission(john, 'myapp.read_book', book)
    >>> True


Unique roles to a given object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a scenario where a model has several roles related to it, but a single user must be assigned to only one of them. In order to allow this behavior, we have the boolean attribute called  ``unique_together``.

Let's say that one user must not be the ``Author`` and the ``Reviewer`` of a given ``Book`` instance at same time. Let's see on the terminal: ::


    # Django Shell

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission
    from myapp.models import Book
    from myapp.roles import Author, Reviewer

    john = User.objects.get(pk=1)
    book = Book.objects.create(title='New Book', content='Much content', my_library=library)

    # John is the Author.
    assign_role(john, Author, book)

    # And also the Reviewer.
    assign_role(john, Reviewer, book)

    # We cannot allow that :(
    has_permission(john, 'myapp.read_book', book)
    >>> True
    has_permission(john, 'myapp.review_book', book)
    >>> True

Now, let's change the class ``RoleOptions`` inside of ``Book``: ::


    # myapp/models.py

    from django.db import models
    from improved_permissions.mixins import RoleMixin

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
            
            # new feature here!
            # --------------------
            unique_together = True
            # --------------------

Going back to the terminal to see the result: ::


    # Django Shell

    from django.contrib.auth.models import User
    from improved_permissions.shortcuts import assign_role, has_permission
    from myapp.models import Book
    from myapp.roles import Author, Reviewer

    john = User.objects.get(pk=1)
    book = Book.objects.create(title='New Book', content='Much content', my_library=library)

    # John is the Author.
    assign_role(john, Author, book)

    # Can be the Reviewer now?
    assign_role(john, Reviewer, book)
    >>> InvalidRoleAssignment: 'The user "john" already has a role attached to the object "book".'

Yeah! Now we are safe.
