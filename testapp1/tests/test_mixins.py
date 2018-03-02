""" mixins tests """
from django.test import TestCase

from improved_permissions.exceptions import NotAllowed
from improved_permissions.models import RolePermission
from improved_permissions.roles import ALL_MODELS, Role, RoleManager
from improved_permissions.shortcuts import get_users
from testapp1.models import Book, Chapter, MyUser, Paragraph
from testapp1.roles import Advisor, Author, Coordenator, Reviewer
from testapp2.models import Library
from testapp2.roles import LibraryOwner


class MixinsTest(TestCase):
    """ mixins test class """

    def setUp(self):
        self.john = MyUser.objects.create(username='john')
        self.bob = MyUser.objects.create(username='bob')
        self.mike = MyUser.objects.create(username='mike')

        self.library = Library.objects.create(title='Cool Library')
        self.book = Book.objects.create(title='Very Nice Book 1', library=self.library)
        self.chapter = Chapter.objects.create(title='Very Nice Chapter 1', book=self.book)
        self.paragraph = Paragraph.objects.create(content='Such Text 1', chapter=self.chapter)

        RoleManager.cleanup()
        RoleManager.register_role(Author)
        RoleManager.register_role(Advisor)
        RoleManager.register_role(Coordenator)
        RoleManager.register_role(Reviewer)
        RoleManager.register_role(LibraryOwner)

    def test_inherit_permission(self):
        """ test if the inherit works fine """

        self.library.assign_role(self.john, LibraryOwner)
        self.book.assign_role(self.bob, Author)

        self.assertTrue(self.bob.has_role(Author))
        self.assertTrue(self.john.has_role(LibraryOwner))

        # Author role assigned to the book, but the chapter
        # and the paragraph are children of book.
        self.assertTrue(self.bob.has_permission('testapp1.add_book', self.book))
        self.assertTrue(self.bob.has_permission('testapp1.add_chapter', self.chapter))
        self.assertTrue(self.bob.has_permission('testapp1.add_paragraph', self.paragraph))

        # As the role Author denies 'review', the
        # children will deny as well.
        self.assertFalse(self.bob.has_permission('testapp1.review', self.book))
        self.assertFalse(self.bob.has_permission('testapp1.review', self.chapter))
        self.assertFalse(self.bob.has_permission('testapp1.review', self.paragraph))

        # Reviewer role assigned to the book, but the chapter
        # and the paragraph are children of book.
        self.book.assign_role(self.mike, Reviewer)
        self.assertTrue(self.mike.has_permission('testapp1.review', self.book))
        self.assertTrue(self.mike.has_permission('testapp1.review', self.chapter))
        self.assertTrue(self.mike.has_permission('testapp1.review', self.paragraph))

        # As the role Reviewer only allows 'review', the
        # children will deny as well.
        self.assertFalse(self.mike.has_permission('testapp1.add_book', self.book))

        # Check if the library owner inherits the permissions from all of them.
        self.assertTrue(self.john.has_permission('testapp1.change_book', self.book))
        self.assertTrue(self.john.has_permission('testapp1.change_book', self.chapter))
        self.assertTrue(self.john.has_permission('testapp1.change_book', self.paragraph))

        self.book.remove_role(self.bob, Author)
        self.library.remove_roles([self.john], LibraryOwner)

    def test_get_users(self):
        """ test if the get_user method works fine """

        # There is no user for the "library" yet.
        self.assertEqual(self.library.get_user(), None)

        self.book.assign_roles([self.bob], Author)
        self.john.assign_role(Advisor, self.bob)
        self.library.assign_role(self.mike, LibraryOwner)

        # Get single user instance.
        result = self.library.get_user()
        self.assertEqual(result, self.mike)

        # Try to get a user from a object with
        # Role class unique=False
        with self.assertRaises(NotAllowed):
            self.book.get_user()

        # Get all users with who is Author of "book".
        self.book.assign_role(self.john, Author)
        result = self.book.get_users(Author)
        self.assertEqual(result, [self.john, self.bob])

        # Get all users with any role to "library".
        result = self.library.get_users()
        self.assertEqual(result, [self.mike])

        # Try to get users list from a object
        # using a wrong Role class.
        with self.assertRaises(NotAllowed):
            self.library.get_users(Advisor)

        # Get all users with any role and any object.
        result = get_users()
        self.assertEqual(result, [self.john, self.bob, self.mike])

        self.john.remove_role(Advisor)
        self.assertFalse(self.john.has_role(Advisor, self.bob))

    def test_get_role(self):
        """ test if the get_role and get_roles methods work fine """
        self.book.assign_role(self.mike, Author)

        self.assertTrue(self.book.has_role(self.mike))
        self.assertTrue(self.book.has_role(self.mike, Author))

        # Check for single role class.
        self.assertEqual(self.mike.get_role(), Author)
        self.assertEqual(self.mike.get_role(self.book), Author)
        self.assertEqual(self.book.get_role(self.mike), Author)  

        self.mike.assign_role(Reviewer, self.book)

        # Check for multiple role class.
        self.assertEqual(self.mike.get_roles(), [Author, Reviewer])
        self.assertEqual(self.mike.get_roles(self.book), [Author, Reviewer])
        self.assertEqual(self.book.get_roles(self.mike), [Author, Reviewer])

    def test_get_objects(self):
        """ test if the get_objects method works fine """
        self.book.assign_role(self.bob, Author)
        self.john.assign_role(Advisor, self.bob)
        self.library.assign_role(self.john, LibraryOwner)

        # Get all objects where john is "Advisor".
        result = self.john.get_objects(Advisor)
        self.assertEqual(result, [self.bob])

        # Get all objects of john for any Role.
        result = self.john.get_objects()
        self.assertEqual(result, [self.library, self.bob])

        # Get all objects of john but only of User model.
        result = self.john.get_objects(model=MyUser)
        self.assertEqual(result, [self.bob])

    def test_get_permissions(self):
        """ test if the get_permissions method works fine """
        self.book.assign_role(self.john, Author)
        self.john.assign_role(Coordenator)

        # Trying to get a permissions list using
        # a object-related role without a object.
        with self.assertRaises(NotAllowed):
            self.john.get_permissions(Author)

        # Trying to get a permissions list using
        # a non object-related role with a object.
        with self.assertRaises(NotAllowed):
            self.john.get_permissions(Coordenator, object)

        self.john.get_permissions(Author, self.book)
        self.john.get_permissions(Coordenator)
