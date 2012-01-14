import os
import sys
import re
import datetime
import dateutil.parser
import hashlib
import Image

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

from ..models.user import User
from ..models.gallery import GalleryContainer, Gallery, \
     GalleryAlbum, GalleryPicture

DEFAULT_ROOT_PASSWORD = 'qwert'

DEFAULT_THUMBNAIL_SIZE = 400, 400
MAX_DISPLAY_WIDTH = 1024
MAX_DISPLAY_HEIGHT = 536

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
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
        populateDB(zodb_root, settings)
        transaction.commit()

def test_populateDB(app_root):
    #user = User('root', 'benjamin.hepp@gmail.com', 'abc')
    album1 = Album('album1', 'this is the first album')
    album2 = Album('album2', 'this is the second album')
    session.add(album1_model)
    session.add(album2_model)
    albums = session.query(AlbumModel).order_by(AlbumModel.name).all()
    for i in xrange(5):
        name = 'picture %d' % i
        description = 'this is picture #%d' % i
        file = 'album1/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, file, file, file,
                                     description, album_id=albums[0].id)
        session.add(picture_model)
    for i in xrange(3):
        name = 'picture %d' % i
        description = 'this is picture #%d' % i
        file = 'album2/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, file, file, file,
                                     description, album_id=albums[1].id)
        session.add(picture_model)
    transaction.commit()

def create_album(category, album_name, date_from, date_to):
    if album_name in category:
        album = category[album_name]
    else:
        print '  creating new album:', album_name
        album = GalleryAlbum(album_name, album_name,
                             ' '.join([album_name]*20),
                             date_from=date_from,
                             date_to=date_to)
        category.add(album)
    #transaction.commit()
    return album

def import_picture(category, album_name, date_from, date_to,
                   picture_name, original_file, display_file,
                   thumbnail_file, img_size, display_size, thumb_size,
                   date):
    album = create_album(category, album_name, date_from, date_to)
    description = picture_name
    print '  adding picture "%s"' % picture_name
    picture = GalleryPicture(picture_name, display_file,
                           original_file, thumbnail_file,
                           description, date=date,
                           original_size=img_size,
                           display_size=display_size,
                           thumbnail_size=thumb_size)
    album.add(picture)
    if category.preview_picture == None:
        category.preview_picture = picture
    if album.preview_picture == None:
        album.preview_picture = picture
    transaction.commit()

def populateDB(zodb_root, settings):
    #password_hash, password_salt = User.hash_password(DEFAULT_ROOT_PASSWORD)
    #user = User('root', 'benjamin.hepp@gmail.com', password_hash, password_salt)
    gallery = Gallery('Photography by Benjamin Hepp')
    category = GalleryContainer('New Zealand', 'Southern Alps - New Zealand')
    gallery.add(category)
    zodb_root['pyGallerid-app-root'] = gallery
    #transaction.commit()

    datematcher = re.compile(r'^([\d]{4}) ([a-zA-Z0-9]{1,9}) ([\d]{1,2})(?:\-([\d]{1,2}))? (.+)$')

    picture_dir = settings['original_picture_dir']
    thumbnail_dir = settings['thumbnail_picture_dir']
    display_dir = settings['display_picture_dir']
    for root, dirs, files in os.walk(picture_dir):
        print 'scanning %s' % root
        for file in files:
            arr = os.path.splitext(file)
            if len(arr) > 1:
                if arr[-1].lower() in \
                    ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                    print '  importing %s' % file
                    album_path = os.path.relpath(root, picture_dir)
                    try:
                        match = datematcher.match(album_path)
                        year, month, day_from, day_to, album_name = match.groups()
                        print year, month, day_from
                        date_from = dateutil.parser.parse(
                            '%s %s %s' % (year, month, day_from)).date()
                        date_to = dateutil.parser.parse(
                            '%s %s %s' % (year, month, day_to)).date()
                    except (AttributeError, ValueError):
                        album_name = album_path
                        date_from = None
                        date_to = None
                    picture_name = arr[0]
                    abs_file = os.path.join(root, file)
                    original_file = os.path.relpath(abs_file, picture_dir)
                    thumbnail_file = original_file
                    abs_thumbnail_file = os.path.join(
                        thumbnail_dir,
                        original_file)
                    display_file = original_file
                    abs_display_file = os.path.join(
                        display_dir,
                        original_file)
                    print '  generating thumbnail'
                    img = Image.open(abs_file)
                    from ExifTags import TAGS
                    info = img._getexif()
                    ret = {}
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        ret[decoded] = value
                    if 'DateTimeOriginal' in ret:
                        date = dateutil.parser.parse(ret['DateTimeOriginal'])
                    elif 'DateTime' in ret:
                        date = dateutil.parser.parse(ret['DateTime'])
                    else:
                        print 'WARNING: No date found!!'
                        for k,v in ret.items():
                            print k, ':', v
                        import sys
                        sys.exit(1)
                        date = None
                    #print 'info:', img.info.keys()
                    #
                    thumb_img = img.copy()
                    thumb_img.thumbnail(DEFAULT_THUMBNAIL_SIZE, Image.ANTIALIAS)
                    if not os.path.exists(os.path.split(abs_thumbnail_file)[0]):
                        os.makedirs(os.path.split(abs_thumbnail_file)[0])
                    thumb_img.save(abs_thumbnail_file)
                    display_img = img.copy()
                    img_width, img_height = img.size
                    scale = MAX_DISPLAY_WIDTH / float(img_width)
                    if scale * img_height > MAX_DISPLAY_HEIGHT:
                        scale = MAX_DISPLAY_HEIGHT / float(img_height)
                    display_size = (int(scale * img_width), int(scale * img_height))
                    display_img.thumbnail(display_size, Image.ANTIALIAS)
                    if not os.path.exists(os.path.split(abs_display_file)[0]):
                        os.makedirs(os.path.split(abs_display_file)[0])
                    display_img.save(abs_display_file)
                    import_picture(
                        category, album_name,
                        date_from, date_to,
                        picture_name,
                        original_file, display_file, thumbnail_file,
                        img.size, display_img.size, thumb_img.size,
                        date)
