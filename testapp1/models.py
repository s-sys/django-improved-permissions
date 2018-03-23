""" testapp1 models """
from django.contrib.auth.models import AbstractUser
from django.db import models

from improved_permissions.mixins import RoleMixin, UserRoleMixin
from testapp2.models import Library


class MyUser(UserRoleMixin, AbstractUser):
    """ MyUser test model """
    class Meta:
        default_permissions = ()
        permissions = (
            ('add_user', 'Add New User'),
            ('change_user', 'Change User'),
            ('delete_user', 'Delete User'),
        )


class Book(RoleMixin, models.Model):
    """ Book test model """
    title = models.CharField(max_length=256)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)

    class Meta:
        permissions = [('view_book', 'View Book'), ('review', 'Review'),]

    class RoleOptions:
        permission_parents = ['library']


class Chapter(RoleMixin, models.Model):
    """ Chapter test model """
    title = models.CharField(max_length=256)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    cited_by = models.ForeignKey(Book, blank=True, null=True, on_delete=models.PROTECT, related_name='citations')

    class Meta:
        permissions = [('view_chapter', 'View Chapter'),]

    class RoleOptions:
        permission_parents = ['book', 'cited_by']


class Paragraph(RoleMixin, models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        permissions = [('view_paragraph', 'View Paragraph'),]

    class RoleOptions:
        permission_parents = ['chapter']


class UniqueTogether(RoleMixin, models.Model):
    content = models.TextField()

    class Meta:
        default_permissions = ()
        permissions = [('nothing', 'Nothing!'),]

    class RoleOptions:
        unique_together = True
