from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)

from ..models import retrieve_gallery
from ..models.user import User


@view_config(context=User)
def user(context, request):
    gallery = retrieve_gallery(context)
    if gallery is not None:
        return HTTPFound(location=request.resource_url(gallery))
    else:
        return HTTPNotFound()
