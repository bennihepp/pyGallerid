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
    if settings.get('wingdbstub', 'false') == 'true':
        import utils.wingdbstub

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
        'pictures/big',
        settings['big_image_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures/regular',
        settings['regular_image_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures/small',
        settings['small_image_dir'],
        cache_max_age=3600
    )
    config.scan()
    return config.make_wsgi_app()
