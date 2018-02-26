""" testapp1 tests """
from django.contrib.auth.models import User
from django.test import TestCase

from improved_permissions import RoleManager
from improved_permissions.shortcuts import has_permission
from testapp1.models import Book, Chapter, Paragraph
from testapp1.roles import Author, Reviewer
from testapp2.models import Library
from testapp2.roles import LibraryOwner


class BookTest(TestCase):
    """ book tests """
    def setUp(self):
        self.john = User.objects.create(username='john')
        self.bob = User.objects.create(username='bob')
        self.mike = User.objects.create(username='mike')

        self.library = Library.objects.create(title='Cool Library')
        self.book1 = Book.objects.create(title='Very Nice Book 1', library=self.library)
        self.chapter1 = Chapter.objects.create(title='Very Nice Chapter 1', book=self.book1)
        self.paragraph1 = Paragraph.objects.create(content='Such Text 1', chapter=self.chapter1)

        RoleManager.register_role(Author)
        RoleManager.register_role(Reviewer)
        RoleManager.register_role(LibraryOwner)

    def test_inherit_permission(self):
        """ test if the inherit works fine """

        self.library.assign_role(self.john, LibraryOwner)

        self.book1.assign_role(self.bob, Author)

        # Author role assigned to the book, but the chapter
        # and the paragraph are children of book.
        self.assertTrue(has_permission(self.bob, 'testapp1.add_book', self.book1))
        self.assertTrue(has_permission(self.bob, 'testapp1.add_chapter', self.chapter1))
        self.assertTrue(has_permission(self.bob, 'testapp1.add_paragraph', self.paragraph1))

        # As the role Author denies 'review', the
        # children will deny as well.
        self.assertFalse(has_permission(self.bob, 'testapp1.review', self.book1))
        self.assertFalse(has_permission(self.bob, 'testapp1.review', self.chapter1))
        self.assertFalse(has_permission(self.bob, 'testapp1.review', self.paragraph1))

        # Reviewer role assigned to the book, but the chapter
        # and the paragraph are children of book.
        self.book1.assign_role(self.mike, Reviewer)
        self.assertTrue(has_permission(self.mike, 'testapp1.review', self.book1))
        self.assertTrue(has_permission(self.mike, 'testapp1.review', self.chapter1))
        self.assertTrue(has_permission(self.mike, 'testapp1.review', self.paragraph1))

        # As the role Reviewer only allows 'review', the
        # children will deny as well.
        self.assertFalse(has_permission(self.mike, 'testapp1.add_book', self.book1))

        # Check if the library owner inherits the permissions from all of them.
        self.assertTrue(self.book1.has_permission(self.john, 'testapp1.change_book'))
        self.assertTrue(self.chapter1.has_permission(self.john, 'testapp1.change_book'))
        self.assertTrue(self.paragraph1.has_permission(self.john, 'testapp1.change_book'))
