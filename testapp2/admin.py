""" testapp2 admin configs """
from django.contrib import admin

from testapp2.models import Library

admin.site.register(Library)
