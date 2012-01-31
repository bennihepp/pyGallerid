# -*- coding: utf-8 -*-

"""
Provides tests for the models of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import unittest
import transaction

from pyramid import testing

from ..models import appmaker
from ..models.user import User
from ..models.gallery import Gallery, GalleryContainer, GalleryAlbum, GalleryPicture

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_my_view(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['project'], 'gallery')

class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine('sqlite:///:memory:')
        DBSession.configure(bind=engine)
        from zope.sqlalchemy import ZopeTransactionExtension
        Base.metadata.create_all(engine)
        with transaction.manager:
            from ..scripts.populate import test_fillDB
            test_fillDB(DBSession())

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_UserModel(self):
        pass
    
    def test_AlbumModel(self):
        pass

    def test_PictureModel(self):
        pass

def run():
    unittest.main()

if __name__ == '__main__':
    run()

