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
    print('usage: %s <config_uri> <username> <category> <album_path>\n'
          '(example: "%s development.ini "New Zealand" '
          'new_pictures")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 5:
        usage(argv)
    config_uri = argv[1]
    username = argv[2]
    category = argv[3]
    album_path = argv[4]
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
        import_pictures(zodb_root, settings, username, category, album_path)
        transaction.commit()


def import_pictures(zodb_root, settings, username, album_path):
    app = appmaker(zodb_root)
    user = retrieve_user(app, username)
    gallery = retrieve_gallery(user)

    container = import_gallery_container(album_path, settings, move_files=True)

    if container is not None:
        gallery.add(container)
        #albums = category.children
        #albums.sort(cmp=lambda x, y: cmp(x.date_from, y.date_from))
        #category.children = albums
