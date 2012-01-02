import os
import sys
import transaction

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
        fillDB(DBSession())

def fillDB(session):
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
