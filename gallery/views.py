from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
    )

from .models import (
    DBSession,
    UserModel,
    AlbumModel,
    PictureModel,
    )

@view_config(route_name='home')
def home(request):
    return HTTPFound(location=request.route_url('list_albums'))

@view_config(route_name='list_albums', renderer='templates/list_albums.mako')
def list_albums(request):
    #one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    albums = DBSession.query(AlbumModel).join(UserModel).\
        filter(AlbumModel.user_id == UserModel.id).\
        all()
        
    return {'one':one, 'project':'gallery'}

