import os
import sys
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
from ..models.gallery import AlbumModel, PictureModel

DEFAULT_ROOT_PASSWORD = 'qwert'

DEFAULT_THUMBNAIL_SIZE = 200, 200

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

def create_album(session, user, album_name):
    if album_name in user.albums:
        album_model = user.albums[album_name]
    else:
        album_model = AlbumModel(album_name, '', user_id=user.id)
        user.albums[album_name] = album_model
    #session.add(album_model)
    #transaction.commit()
    #album_model = session.query(AlbumModel).filter(AlbumModel.name == album_name).first()
    return album_model

def import_picture(session, user, album_name, picture_name, original_file, thumbnail_file):
    album = create_album(session, user, album_name)
    description = ''
    display_file = original_file
    print '  adding picture "%s"' % picture_name
    picture_model = PictureModel(picture_name, display_file,
                                 original_file, thumbnail_file,
                                 description, album_id=album.id)
    album.pictures[picture_name] = picture_model
    #session.add(picture_model)

def fillDB(session, settings):
    password_hash, password_salt = UserModel.hash_password(DEFAULT_ROOT_PASSWORD)
    user_model = UserModel('root', 'benjamin.hepp@gmail.com', password_hash, password_salt)
    session.add(user_model)
    #transaction.commit()
    #user_model = DBSession.query(UserModel).filter(UserModel.name == 'root').first()

    pictures_dir = settings['pictures_dir']
    thumbnails_dir = settings['thumbnails_dir']
    for root, dirs, files in os.walk(pictures_dir):
        print 'scanning %s' % root
        for file in files:
            arr = os.path.splitext(file)
            if len(arr) > 1:
                if arr[-1].lower() in \
                    ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                    print '  importing %s' % file
                    album_name = os.path.relpath(root, pictures_dir)
                    picture_name = arr[0]
                    abs_file = os.path.join(root, file)
                    original_file = os.path.relpath(abs_file, pictures_dir)
                    thumbnail_file = original_file
                    abs_thumbnail_file = os.path.join(
                        thumbnails_dir,
                        original_file)
                    print '  generating thumbnail'
                    img = Image.open(abs_file)
                    """print 'info:', img.info.keys()
                    from PIL.ExifTags import TAGS
                    info = img._getexif()
                    ret = {}
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        ret[decoded] = value
                    print ret"""
                    img.thumbnail(DEFAULT_THUMBNAIL_SIZE, Image.ANTIALIAS)
                    if not os.path.exists(os.path.split(abs_thumbnail_file)[0]):
                        os.makedirs(os.path.split(abs_thumbnail_file)[0])
                    img.save(abs_thumbnail_file)
                    import_picture(
                        session, user_model,
                        album_name, picture_name,
                        original_file, thumbnail_file)
    transaction.commit()
