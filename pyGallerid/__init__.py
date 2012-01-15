from pyramid.config import Configurator
from pyramid_zodbconn import get_connection

from.models import appmaker

# This is only needed when using SQLAlchemy
#from sqlalchemy import engine_from_config
#from .models import DBSession


def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if settings.get('debug', 'false') == 'true':
        import wingdbstub

    config = Configurator(root_factory=root_factory, settings=settings)
    # This is only needed when using SQLAlchemy
    #engine = engine_from_config(settings, 'sqlalchemy.')
    #DBSession.configure(bind=engine)
    config.add_static_view(
        'static',
        settings['static_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures/original',
        settings['original_picture_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures/display',
        settings['display_picture_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures/thumbnails',
        settings['thumbnail_picture_dir'],
        cache_max_age=3600
    )
    config.scan()
    return config.make_wsgi_app()
