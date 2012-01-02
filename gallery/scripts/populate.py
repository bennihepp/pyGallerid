import os
import sys
from PIL import Image
import transaction

THUMBNAIL_SIZE = 200, 200

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models import DBSession, Base
from ..models.user import UserModel
from ..models.gallery import AlbumModel, PictureModel

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
        fillDB(DBSession(), settings)

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
        url = 'album1/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, url, url, url,
                                     description, album_id=albums[0].id)
        session.add(picture_model)
    for i in xrange(3):
        name = 'picture %d' % i
        description = 'this is picture #%d' % i
        url = 'album2/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, url, url, url,
                                     description, album_id=albums[1].id)
        session.add(picture_model)
    transaction.commit()

def import_photo(album_name, photo_name, original_url, thumbnail_url):
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
        url = 'album1/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, url, url, url,
                                     description, album_id=albums[0].id)
        session.add(picture_model)
    for i in xrange(3):
        name = 'picture %d' % i
        description = 'this is picture #%d' % i
        url = 'album2/pictures/%d.jpeg' % i
        picture_model = PictureModel(name, url, url, url,
                                     description, album_id=albums[1].id)
        session.add(picture_model)
    transaction.commit()

def fillDB(session, settings):
    photos_dir = settings['photos_dir']
    thumbnails_dir = settings['thumbnails_dir']
    for root, dirs, files in os.walk(photos_dir):
        print 'scanning %s' % root
        for file in files:
            arr = os.path.splitext(file)
            if len(arr) > 1:
                if arr[-1].lower() in \
                    ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                    print '  importing %s' % file
                    album_name = root
                    photo_name = arr[0]
                    original_url = os.path.join(root, file)
                    thumbnail_url = os.path.join(
                        thumbnails_dir,
                        os.path.relpath(original_url, photos_dir))
                    print '  generating thumbnail'
                    img = Image.open(original_url)
                    print 'info:', img.info.keys()
                    from PIL.ExifTags import TAGS
                    info = img._getexif()
                    ret = {}
                    for tag, value in info.items():
                        decoded = TAGS.get(tag, tag)
                        ret[decoded] = value
                    print ret
                    img.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                    if not os.path.exists(os.path.split(thumbnail_url)[0]):
                        os.makedirs(os.path.split(thumbnail_url)[0])
                    img.save(thumbnail_url)
                    import_photo(album_name, photo_name,
                                 original_url, thumbnail_url)
