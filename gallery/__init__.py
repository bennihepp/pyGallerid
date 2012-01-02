from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('photos', settings['photos_dir'], cache_max_age=3600)
    config.add_static_view('thumbnails', settings['thumbnails_dir'], cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('view_picture',
                     '/{username}/gallery/pictures/{album_name}/{picture_name}')
    config.add_route('view_album', '/{username}/gallery/albums/{album_name}')
    config.add_route('view_gallery', '/{username}/gallery')
    config.scan()
    return config.make_wsgi_app()
