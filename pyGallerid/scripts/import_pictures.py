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
import logging

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
from pyramid.traversal import find_resource

from ..models import appmaker, retrieve_user, retrieve_gallery
from ..models.gallery import GalleryContainer
from ..utils.picture import import_gallery_container

logger = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <resource_path> <path> <sorting_order>\n'
          '(example: "%s development.ini Europe new_pictures'
          ' [text|number|date]' \
          % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)
    config_uri = argv[1]
    resource_path = argv[2]
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
        import_pictures(zodb_root, settings, resource_path,
                        path, sorting_order)
        transaction.commit()


def import_pictures(zodb_root, settings, resource_path, path, sorting_order):
    username = settings['default_user']
    app = appmaker(zodb_root)
    user = retrieve_user(app, username)
    gallery = retrieve_gallery(user)
    resource = find_resource(gallery, resource_path)
    logger.info('found resource: %s' % resource.name)
    assert isinstance(resource, GalleryContainer)

    normpath = os.path.normpath(path)
    cwd = os.getcwd()
    os.chdir(os.path.split(normpath)[0])
    basepath = os.path.basename(normpath)

    container = import_gallery_container(basepath, resource_path, settings,
                                         move_files=False,
                                         sorting_order=sorting_order)

    os.chdir(cwd)

    if container is not None:
        resource.add(container)
        #for child in container.values():
        #    resource.add(child)
        #albums = category.children
        #albums.sort(cmp=lambda x, y: cmp(x.date_from, y.date_from))
        #category.children = albums

