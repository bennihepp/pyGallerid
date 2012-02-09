# -*- coding: utf-8 -*-

"""
Script for initializing the pyGallerid database.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os
import sys

# this is not documented in the pyramid 1.3 documentation,
# so if it disappears at some point just use repoze.zodbconn
# or connect to the ZODB directly
from pyramid_zodbconn import db_from_uri

#import repoze.zodbconn.uri
#from ZODB.FileStorage import FileStorage
#from ZODB.DB import DB

import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import appmaker, retrieve_user, retrieve_gallery, retrieve_about
from ..models.user import User
from ..models.gallery import Gallery, GalleryDocument


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <email> '
          '<password> [<description>]\n'
          '(example: "%s development.ini myname '
          'mymail@mydomain.com qwerty)' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    # for SQLalchemy
    #engine = engine_from_config(settings, 'sqlalchemy.')
    #DBSession.configure(bind=engine)
    #Base.metadata.create_all(engine)
    db = db_from_uri(settings['zodbconn.uri'])
    # for ZODB without repoze.zodbconn
    #storage = FileStorage(settings['zodbconn.file'])
    #db = DB(storage)
    conn = db.open()
    zodb_root = conn.root()
    with transaction.manager:
        remove_pictures(zodb_root, settings)
        transaction.commit()


def remove_pictures(zodb_root, settings):
    username = settings['default_user']
    app = appmaker(zodb_root)
    user = retrieve_user(app, username)
    if user is None:
        raise ValueError("No such user: %s " % username)
    gallery = retrieve_gallery(user)
    if gallery is None:
        raise ValueError("The user %s already has no gallery" % username)
    path = "Europe/St. Antoenien"
    picture_prefix = '...'
    pictures = [('St. Antoenien-%d' % i) for i in (2, 6, 8, 18, 19, 24, 28, 34, 35, 36, 37, 38, 39, 40, 41)]
    from pyramid.traversal import find_resource
    for picture in pictures:
        resource = find_resource(gallery, os.path.join(path, picture))
        if resource is None:
            raise Exception("Couldn't find picture: %s" % picture)
        print "Removing picture %s" % picture
        resource.parent = None

