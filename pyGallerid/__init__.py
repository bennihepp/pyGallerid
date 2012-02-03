# -*- coding: utf-8 -*-

"""
Creates the pyGallerid WSGI application instance.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp

from pyramid.config import Configurator
from pyramid_zodbconn import get_connection, db_from_uri
from pyramid.settings import asbool
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid_beaker import session_factory_from_settings, \
                           set_cache_regions_from_settings

from models import appmaker, __sw_version__

# This is only needed when using SQLAlchemy
#from sqlalchemy import engine_from_config
#from .models import DBSession

__version__ = 0.2


def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def evolve_database(root, sw_version, initial_db_version=0):
    from repoze.evolution import ZODBEvolutionManager, evolve_to_latest
    manager = ZODBEvolutionManager(
        root, evolve_packagename='pyGallerid.evolve',
        sw_version=sw_version,
        initial_db_version=initial_db_version
    )
    evolve_to_latest(manager)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if asbool(settings.get('wingdbstub', 'false')):
        import misc.wingdbstub

    # evolve ZODB database to latest version
    db = db_from_uri(settings['zodbconn.uri'])
    conn = db.open()
    evolve_database(appmaker(conn.root()), __sw_version__)
    db.close()

    # set up beaker session
    session_factory = session_factory_from_settings(settings)
    # set up beaker cache
    set_cache_regions_from_settings(settings)

    config = Configurator(root_factory=root_factory, settings=settings)

    config.include(set_auth_policies)

    config.include(add_user_property)

    # include pyramid plugins
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_zodbconn')
    config.include('pyramid_rewrite')

    # register beaker session factory
    config.set_session_factory(session_factory)

    # This is only needed when using SQLAlchemy
    #engine = engine_from_config(settings, 'sqlalchemy.')
    #DBSession.configure(bind=engine)

    # add static views
    config.include(add_static_views)

    # scan for declarative configurations
    config.scan()

    # add url rewriting rules
    config.include(add_rewrite_rules)

    # return WSGI application instance
    return config.make_wsgi_app()


def add_user_property(config):
    from pyramid.traversal import find_root
    from pyramid.security import authenticated_userid
    from models import retrieve_user

    # add user property to request objects
    def get_user(request):
        root = find_root(request.context)
        username = authenticated_userid(request)
        user = retrieve_user(root, username)
        return user
    config.set_request_property(get_user, 'user', reify=True)


def set_auth_policies(config):
    from models.user import groupfinder
    # set up authentication and authorization
    authn_policy = SessionAuthenticationPolicy(callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)


def add_rewrite_rules(config):
    # add rewrite rule for /
    pattern = r'/'
    target = '/%s/gallery/' % config.registry.settings['default_user']
    config.add_rewrite_rule(pattern, target)
    # add rewrite rule for /favicon.ico
    pattern = r'/favicon.ico'
    target = '/static/favicon.ico'
    config.add_rewrite_rule(pattern, target)
    # add rewrite rule for /about
    pattern = r'/about'
    target = '/%s/about/' % config.registry.settings['default_user']
    config.add_rewrite_rule(pattern, target)
    # add rewrite rule for /gallery/*/
    pattern = r'/gallery/(?P<subpath>.*)'
    target = '/%s/gallery/%%(subpath)s' \
        % config.registry.settings['default_user']
    config.add_rewrite_rule(pattern, target)


def add_static_views(config):
    settings = config.registry.settings
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
