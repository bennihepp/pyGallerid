# -*- coding: utf-8 -*-

"""
Script for importing pictures into the pyGallerid database.
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

from ..models import appmaker, retrieve_user, retrieve_gallery
from ..utils.picture import import_gallery_container


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <username> <path> <sorting_order>\n'
          '(example: "%s development.ini hepp new_pictures [text|number|date]' \
          % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)
    config_uri = argv[1]
    username = argv[2]
    path = argv[3]
    sorting_order = 'number'
    if len(argv) > 4:
        sorting_order = argv[4]
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
        import_pictures(zodb_root, settings, username, path, sorting_order)
        transaction.commit()


def import_pictures(zodb_root, settings, username, path, sorting_order):
    app = appmaker(zodb_root)
    user = retrieve_user(app, username)
    gallery = retrieve_gallery(user)

    cwd = os.getcwd()
    os.chdir(path)

    container = import_gallery_container('.', settings, move_files=False, sorting_order=sorting_order)

    os.chdir(cwd)

    if container is not None:
        for child in container:
            gallery.add(child)
        #albums = category.children
        #albums.sort(cmp=lambda x, y: cmp(x.date_from, y.date_from))
        #category.children = albums

