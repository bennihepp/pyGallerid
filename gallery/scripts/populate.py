import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Base,
    UserModel,
    AlbumModel,
    PictureModel,
    )

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
    with transaction.manager as tm:
        session = DBSession
        user_model = UserModel('hepp', 'benjamin.hepp@gmail.com', 'abc')
        session.add(user_model)
        print 'user_model:', user_model.id
        tm.commit()
        print user_model.id
    with transaction.manager:
        album1_model = AlbumModel('album1', user_model.id, 'this is the first album')
        album2_model = AlbumModel('album2', user_model.id, 'this is the second album')
        session.add(album1_model)
        session.add(album2_model)
        transaction.commit()
        for i in xrange(5):
            name = 'picture %d' % i
            description = 'this is picture #%d' % i
            url = 'album1/pictures/%d.jpeg' % i
            picture_model = PictureModel(url, url, url, name,
                                         description, album1_model.id)
            session.add(picture_model)
        for i in xrange(3):
            name = 'picture %d' % i
            description = 'this is picture #%d' % i
            url = 'album2/pictures/%d.jpeg' % i
            picture_model = PictureModel(url, url, url, name,
                                         description, album2_model.id)
            session.add(picture_model)
    
