Setup
=====

Installation
************
We are in PyPI. Just use the following command within your development environment: ::

    pip install django-improved-permissions


Configuration
*************

We use some apps that are already present in Django: ``auth`` and ``contenttypes``. Probably they are already declared, but just make sure so we don't have any issues later. ::

    # settings.py

    INSTALLED_APPS = (
    ...
    'django.contrib.auth',
    'django.contrib.contenttypes',
    ...
    )

Now, you need to add our app inside your Django project. To do this, add ``improved_permissions`` into your ``INSTALLED_APPS``::

    # settings.py

    INSTALLED_APPS = (
    ...
    'improved_permissions',
    ...
    )

.. note:: We are almost there! We use some tables in the database to store the permissions, so you must run ``./manage.py migrate improved_permissions`` in order to migrate all models needed.

Yeah, all set to start! Let's go to the next page to get a quick view of how everything works.
