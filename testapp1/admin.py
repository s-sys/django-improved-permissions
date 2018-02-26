""" testapp1 admin configs """
from django.contrib import admin

from testapp1.models import Book, Chapter, Paragraph

admin.site.register(Book)
admin.site.register(Chapter)
admin.site.register(Paragraph)
