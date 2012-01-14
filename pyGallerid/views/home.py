from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)
from pyramid.response import Response

@view_config(route_name='home')
def home(context, request):
    return Response("Hello")
    #return HTTPFound(location=request.route_url('view_album_gallery', username='root'))
