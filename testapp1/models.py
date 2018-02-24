from django.db import models

from testapp2.models import Library

class Book(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    library = models.ForeignKey(Library, on_delete=models.PROTECT)

    class Permissions:
        permissions = ('view_book',)


class Chapter(models.Model):
    title = models.CharField(max_length=256)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Permissions:
        permissions = ('view_chapter',)
        permission_parents = ['book']


class Paragraph(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    content = models.TextField()

    class Permissions:
        permissions = ('view_paragraph',)
        permission_parents = ['chapter']
