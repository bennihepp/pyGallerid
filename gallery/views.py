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
    return HTTPFound(location=request.route_url('list_albums', username='hepp'))

@view_config(route_name='list_albums', renderer='list_albums.mako')
def list_albums(request):
    #one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    username = request.matchdict['username']
    albums = DBSession.query(AlbumModel).join(UserModel).\
        filter(AlbumModel.user_id == UserModel.id).\
        filter(UserModel.name == username).\
        all()
    #albums = DBSession.query(AlbumModel).\
    #    all()
        
    #return {'one':one, 'project':'gallery'}
    return {'username' : username, 'albums' : albums}

