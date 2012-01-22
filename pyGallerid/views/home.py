from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)

from ..models import retrieve_user, retrieve_gallery, PersistentContainer


@view_config(context=PersistentContainer)
def home(context, request):
    user = retrieve_user(context, 'hepp')
    gallery = retrieve_gallery(user)
    if gallery is not None:
        return HTTPFound(location=request.resource_url(gallery))
    else:
        return HTTPNotFound()
