from django.db import models

from testapp2.models import Library


class Book(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    library = models.ForeignKey(Library, on_delete=models.PROTECT)

    class Meta:
        permissions = [('view_book', 'Visualizar Livro'),]

    class RoleOptions:
        permission_parents = ['library']


class Chapter(models.Model):
    title = models.CharField(max_length=256)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        permissions = [('view_chapter', 'Visualizar Capítulo'),]

    class RoleOptions:
        permission_parents = ['book']


class Paragraph(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        permissions = [('view_paragraph', 'Visualizar Parágrafo'),]

    class RoleOptions:
        permission_parents = ['chapter']
