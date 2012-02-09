# -*- coding: utf-8 -*-

"""
Provides tests for the models of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os
import unittest
import transaction

from pyramid import testing
from pyramid.traversal import find_resource

from ..models import PersistentContainer, appmaker
from ..models.user import User, groupfinder
from ..models.gallery import GalleryResource, Gallery, GalleryContainer, \
     GalleryAlbum, GalleryPicture, GalleryDocument, GalleryAbout, \
     GalleryImageView, GalleryImageFile


# TODO: create a real ZODB in memory
class DummyDB(object):
    def __init__(self):
        self.init_dummy_db()

    def init_dummy_db(self):
        self.root = {}
        self.app = appmaker(self.root)
        assert isinstance(self.app, PersistentContainer)
        # add users
        name = 'foo'
        email = 'foo@bla.com'
        password = 'qwerty'
        user1 = User('foo', 'foo@bla.com', 'qwerty')
        user2 = User('moo', 'moo@bla.com', 'asdfg')
        self.app.add(user1)
        self.app.add(user2)
        # add gallery
        gallery = Gallery('Foo\'s gallery', 'foo/pictures/', user1)
        user1.add(gallery)
        # add gallery about document
        about = GalleryAbout('About', 'About foo\'s gallery')
        gallery.add(about)
        # add gallery container
        container = GalleryContainer('Europe', 'Europe', path='europe')
        gallery.add(container)
        # add gallery albums
        album1 = GalleryAlbum('Christmas', 'Christmas party', '...',
                             path='christmas')
        album2 = GalleryAlbum('Rome', 'Holiday in Rome', '...',
                              path='rome')
        gallery.add(album1)
        container.add(album2)
        # add pictures
        # TODO

    def dummy_root_factory(self, request):
        return appmaker(self.root)


class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.db = DummyDB()
        self.config.set_root_factory(self.db.dummy_root_factory)

    def tearDown(self):
        testing.tearDown()

    def test_UserModel(self):
        name = 'foo'
        email = 'foo@bla.com'
        password = 'qwerty'
        wrong_password = 'qwertz'
        user = User(name, email, password)
        self.assertTrue(user.authenticate(password))
        self.assertFalse(user.authenticate(wrong_password))
        pw_hash, pw_salt = user.password_hash, user.password_salt
        user.change_password(password)
        # theoretically this could be true, but it's just too unlikely
        self.assertNotEqual(pw_hash, user.password_hash)
        self.assertNotEqual(pw_salt, user.password_salt)

    def test_AlbumModel(self):
        name = 'Christmas'
        description = 'Christmas party'
        long_description = '...'
        path = 'christmas'
        album = GalleryAlbum(name, description, long_description, path=path)
        self.assertEqual(album.absolute_path, path)
        self.assertEqual(album.absolute_path_tuple, (path,))
        self.assertIsNone(album.preview_picture)
        self.assertEqual(len(album.pictures), 0)

    def test_PictureModel(self):
        name = 'Tree'
        big_image = GalleryImageFile('big.jpeg', size=(800,600))
        regular_image = GalleryImageFile('regular.jpeg', size=(400,300))
        small_image = GalleryImageFile('small.jpeg', size=(200,150))
        big_view = GalleryImageView(big_image)
        regular_view = GalleryImageView(regular_image)
        small_view = GalleryImageView(small_image)
        picture = GalleryPicture(name, big_view, regular_view, small_view)
        self.assertEqual(picture.big_image_path, 'big.jpeg')
        self.assertEqual(picture.regular_image_path, 'regular.jpeg')
        self.assertEqual(picture.small_image_path, 'small.jpeg')
        self.assertEqual(picture.big_image_view.width, big_image.width)
        self.assertEqual(picture.regular_image_view.width,
                         regular_image.width)
        self.assertEqual(picture.small_image_view.width, small_image.width)

    def test_AlbumModelDB(self):
        path = '/foo/gallery/Europe/Rome'
        request = testing.DummyRequest(path=path)
        root = self.db.dummy_root_factory(request)
        rome = find_resource(root, path)
        self.assertIsInstance(rome, GalleryAlbum)
        self.assertEqual(rome.name, 'Rome')
        self.assertIsInstance(rome.parent, GalleryContainer)
        self.assertEqual(rome.parent.name, 'Europe')
        assert isinstance(rome, GalleryAlbum)
        path_tuple = ('foo/pictures', 'europe', 'rome')
        self.assertEqual(rome.absolute_path_tuple, path_tuple)
        self.assertEqual(rome.absolute_path, os.path.join(*path_tuple))


def run():
    unittest.main()


if __name__ == '__main__':
    run()
