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
    if len(argv) < 4:
        usage(argv)
    config_uri = argv[1]
    email = argv[2]
    password = argv[3]
    if len(argv) > 4:
        description = argv[4]
    else:
        description = "Benjamin Hepp's Photography"
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
        create_gallery(zodb_root, settings, email,
                       password, description)
        transaction.commit()


def create_gallery(zodb_root, settings, email,
                   password, description):
    username = settings['default_user']
    app = appmaker(zodb_root)
    user = retrieve_user(app, username)
    if user is not None:
        raise ValueError("A user with name %s already exists" % username)
    #password_hash, password_salt = User.hash_password(password)
    #user = User(username, email, password_hash, password_salt)
    user = User(username, email, password)
    app.add(user)
    gallery = retrieve_gallery(user)
    if gallery is not None:
        raise ValueError("The user %s already has a gallery" % username)
    gallery = Gallery(description, user=user, path=settings['image_dir'])
    user.add(gallery)
    about = retrieve_about(user)
    if about is not None:
        raise ValueError("The user %s already has an about page" % username)
    about = GalleryDocument('about', 'About', 'Description')
    user.add(about)
