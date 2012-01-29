import os

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from pyramid.settings import asbool
from pyramid_beaker import session_factory_from_settings, \
                           set_cache_regions_from_settings

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
    if asbool(settings.get('wingdbstub', 'false')):
        import utils.wingdbstub

    # set up beaker session
    session_factory = session_factory_from_settings(settings)
    # set up beaker cache
    set_cache_regions_from_settings(settings)

    config = Configurator(root_factory=root_factory, settings=settings)

    # include pyramid plugins
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_zodbconn')

    # register beaker session factory
    config.set_session_factory(session_factory)

    # This is only needed when using SQLAlchemy
    #engine = engine_from_config(settings, 'sqlalchemy.')
    #DBSession.configure(bind=engine)

    config.add_static_view(
        'static',
        settings['static_dir'],
        cache_max_age=3600
    )
    config.add_static_view(
        'pictures',
        settings['image_dir'],
        cache_max_age=3600
    )

    config.scan()

    return config.make_wsgi_app()

