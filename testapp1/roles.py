""" testapp1 roles """
from improved_permissions import roles
from testapp1.models import Book, Chapter, Paragraph


class Author(roles.Role):
    verbose_name = 'Autor'
    models = [Book, Chapter, Paragraph]
    deny = ['testapp1.review']


class Reviewer(roles.Role):
    verbose_name = 'Revisor'
    models = [Book]
    allow = ['testapp1.review']
    inherit = True
    inherit_allow = ['testapp1.review']
