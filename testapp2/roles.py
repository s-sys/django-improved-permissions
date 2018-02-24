from improved_permissions import roles
from testapp2.models import Library

class LibraryOwner(roles.Role):
    verbose_name = 'Biblioterário'
    model = Library
    inherit = True
