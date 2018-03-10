Role Class
==========

Role classes must be implemented by inheriting the ``Role`` class present in ``improved_permissions.roles``. 

Whenever you start your project, they are automatically validated and can already be used. If something is wrong, ``RoleManager`` will raise an exception with a message explaining the cause of the error.

.. note:: Only Role classes inside modules called ``roles.py`` are automatically validated. See here to change this behavior.


Required attributes
*******************

The ``Role`` class has some attributes that are required to be properly registered by our ``RoleManager``. The description of these attributes is in the following table:

===================== ========================== ===
Attribute             Type                       Description
===================== ========================== ===
``verbose_name``      ``str``                    Used to print some information about the role.
``models``            ``list`` or ``ALL_MODELS`` Defines which models this role can be attached.
``allow`` or ``deny`` ``list``                   Defines which permissions should be allowed or denied. You must define only one of them.
===================== ========================== ===

Optional Attributes
*******************

The ``Role`` class also has other attributes, which are considered as optional. When they are not declared, we assign default values for these arguments.

===================================== ======== ========= ===
Attribute                             Type     Default   Description
===================================== ======== ========= ===
``unique``                            ``bool`` ``False`` Only one User instance is allowed to be attached to a given object using this role.
``inherit``                           ``bool`` ``False`` Allows this role to inherit permissions from its child models. Read about this feature here.
``inherit_allow`` or ``inherit_deny`` ``list`` ``[]``    Specifies which inherit permissions should be allowed or denied. You must define only one of them.
===================================== ======== ========= ===

Role Classes using ALL_MODELS
*****************************

If you need a role that manages any model of your project, you can define the ``models`` attribute using ``ALL_MODELS``. These classes are ``inherit=True`` by default because they don't have their own permissions, only inherited permissions. For example: ::

    # myapp/roles.py

    from improved_permissions.roles import ALL_MODELS, Role

    class SuperUser(Role):
        verbose_name = 'Super Man Role'
        models = ALL_MODELS
        deny = []
        inherit_deny = []

Because this class is not attached to a specific model, you can use the shortcuts without defining objects. For example: ::

    from myapp.models import Book
    from myapp.roles import SuperUser

    john = User.objects.get(pk=1)
    book = Book.objects.create(title='Nice Book', content='Such content.')

    # You shouldn't pass an object during assignment.
    assign_role(john, SuperUser)

    # This line will raise an InvalidRoleAssignment exception
    assign_role(john, SuperUser, book)

    # You can check with and without an object.
    has_permission(john, 'myapp.read_book')
    >>> True
    has_permission(john, 'myapp.read_book', book)
    >>> True

Public Methods
**************

The role classes have some class methods that you can call if you need them.

.. function:: get_verbose_name(): str

Returns the ``verbose_name`` attribute. Example: ::

    from myapp.roles import Author, Reviewer

    Author.get_verbose_name()
    >>> 'Author'
    Reviewer.get_verbose_name()
    >>> 'Reviewer'

.. function:: is_my_model(model): bool

Checks if the role can be attached to the argument ``model``. The argument can be either the model class or an instance. Example: ::

    from myapp.models import Book
    from myapp.roles import Author

    Author.is_my_model('some data')
    >>> False
    Author.is_my_model(Book)
    >>> True
    my_book = Book.objects.create(title='Nice Book', content='Nice content.')
    Author.is_my_model(my_book)
    >>> True

.. function:: get_models(): list

Returns a list of all model classes which this role can be attached. If the ``models`` attribute was defined using ``ALL_MODELS``, this method will return a list of all valid models of the project. For example: ::

    from myapp.models import Book
    from myapp.roles import Author, SuperUser

    Author.get_models()
    >>> [Book]
    SuperUser.get_models()
    >>> [Book, User, Permission, ContentType, ...] # all models known by Django

In the next section, we describe all existing shortcuts in this app.
