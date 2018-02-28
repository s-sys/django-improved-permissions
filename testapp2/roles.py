""" testapp2 roles """
from improved_permissions import roles
from testapp2.models import Library


class LibraryOwner(roles.Role):
    verbose_name = 'Biblioterário'
    models = [Library]
    unique = True
    deny = []
    inherit = True
    inherit_deny = ['testapp1.review']
