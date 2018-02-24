from improved_permissions import roles
from testapp1.models import Book, Chapter, Paragraph


class Author(roles.Role):
    verbose_name = 'Autor'
    models = [Book, Chapter, Paragraph]
    inherit = True
