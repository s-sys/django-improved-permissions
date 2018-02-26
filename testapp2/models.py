""" testapp2 models """
from django.db import models

from improved_permissions.mixins import RoleMixin


class Library(RoleMixin, models.Model):
    title = models.CharField(max_length=256)
