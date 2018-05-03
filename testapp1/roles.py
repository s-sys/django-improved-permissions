""" testapp1 roles """
from improved_permissions.roles import ALL_MODELS, Role
from testapp1.models import Book, Chapter, MyUser, Paragraph


class Author(Role):
    verbose_name = 'Author'
    models = [Book, Chapter, Paragraph]
    deny = ['testapp1.review']


class Reviewer(Role):
    verbose_name = 'Reviewer'
    models = [Book]
    allow = ['testapp1.review']
    inherit = True
    inherit_allow = ['testapp1.review']


class Advisor(Role):
    verbose_name = "Advisor"
    models = [MyUser]
    unique = True
    deny = []


class Coordenator(Role):
    verbose_name = "Coordenator"
    models = ALL_MODELS
    inherit_deny = ['testapp1.change_user']
