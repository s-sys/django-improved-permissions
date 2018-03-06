Setup
=====

Instalation
^^^^^^^^^^^

This is how you install::

	pip install django-improved-permissions


Configuration
^^^^^^^^^^^^^

Add ``improved_permissions`` into your ``INSTALLED_APPS``::

	INSTALLED_APPS = (
	...
	'improved_permissions',
	...
	)


Now, run ``./manage.py migrate improved_permissions`` in order to migrate the models needed.
