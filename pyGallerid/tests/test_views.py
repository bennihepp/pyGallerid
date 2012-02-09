# -*- coding: utf-8 -*-

"""
Provides tests for the views of pyGallerid.
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


def run():
    unittest.main()


if __name__ == '__main__':
    run()

