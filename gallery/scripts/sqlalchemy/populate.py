import os
import sys
import re
import datetime
import dateutil.parser
import hashlib
from PIL import Image
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import DBSession, Base
from ..models.user import UserModel
from ..models.gallery import CategoryModel, AlbumModel, PictureModel

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
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        fillDB(DBSession, settings)

def test_fillDB(session):
    user_model = UserModel('root', 'benjamin.hepp@gmail.com', 'abc')
    session.add(user_model)
    transaction.commit()
    user_model = session.query(UserModel).all()[0]
    album1_model = AlbumModel('album1', 'this is the first album', user_id=user_model.id)
    album2_model = AlbumModel('album2', 'this is the second album', user_id=user_model.id)
    session.add(album1_model)
    session.add(album2_model)
    transaction.commit()
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

def create_album(session, category, album_name, date_from, date_to):
    if album_name in category.album_dict:
        album_model = category.album_dict[album_name]
    else:
        print '  creating new album:', album_name
        album_model = AlbumModel(album_name, '', date_from=date_from,
                                 date_to=date_to, category_id=category.id)
        category.album_dict[album_name] = album_model
    #session.add(album_model)
    #transaction.commit()
    #album_model = session.query(AlbumModel).filter(AlbumModel.name == album_name).first()
    return album_model

def import_picture(session, category, album_name, date_from, date_to,
                   picture_name, original_file, display_file,
                   thumbnail_file, img_size, display_size, thumb_size,
                   date):
    album = create_album(session, category, album_name, date_from, date_to)
    description = picture_name
    print '  adding picture "%s"' % picture_name
    picture_model = PictureModel(picture_name, display_file,
                                 original_file, thumbnail_file,
                                 description, date=date,
                                 original_size=img_size,
                                 display_size=display_size,
                                 thumbnail_size=thumb_size,
                                 album_id=album.id)
    album.picture_dict[picture_name] = picture_model
    if category.preview_picture == None:
        category.preview_picture = picture_model
    if album.preview_picture == None:
        album.preview_picture = picture_model
    #session.add(picture_model)

def fillDB(session, settings):
    password_hash, password_salt = UserModel.hash_password(DEFAULT_ROOT_PASSWORD)
    user_model = UserModel('root', 'benjamin.hepp@gmail.com', password_hash, password_salt)
    category_model = CategoryModel('New Zealand', 'Southern Alps - New Zealand')
    category_model.user = user_model
    session.add(user_model)
    #transaction.commit()
    #user_model = DBSession.query(UserModel).filter(UserModel.name == 'root').first()

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
                    from PIL.ExifTags import TAGS
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
                    #print ret
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
                        session, category_model,
                        album_name, date_from, date_to,
                        picture_name, original_file,
                        display_file, thumbnail_file,
                        img.size, display_img.size, thumb_img.size,
                        date)
    transaction.commit()
