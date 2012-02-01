# -*- coding: utf-8 -*-

"""
Provides views for the root resource and the favicon of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)

from ..models import retrieve_user, retrieve_gallery, PersistentContainer


## Load favicon.ico
#_here = os.path.dirname(__file__)
#_icon = open(os.path.join(_here, '../static', 'favicon.ico')).read()
#_icon_response = Response(content_type='image/x-icon', body=_icon)


#@view_config(name='favicon.ico')
#def favicon_view(context, request):
    #return _icon_response


#@view_config(context=PersistentContainer)
#def root(context, request):
    #user = retrieve_user(
        #context, request.registry.settings.get('default_user', 'root')
    #)
    #gallery = retrieve_gallery(user)
    #if gallery is not None:
        #return HTTPFound(location=request.resource_url(gallery))
    #else:
        #return HTTPNotFound()
