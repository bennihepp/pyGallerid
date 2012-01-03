from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)
from pyramid.response import Response

from ..models import DBSession
from ..models.user import UserModel
from ..models.gallery import AlbumModel, PictureModel

def create_menu_urls(context, request):
    menu_urls = {}
    if 'username' in request.matchdict:
        menu_urls['Gallery'] = request.route_url('view_gallery', **request.matchdict)
        if 'album_name' in request.matchdict:
            menu_urls['Album %s' % request.matchdict['album_name']] = \
                request.route_url('view_album', **request.matchdict)
    return menu_urls

@view_config(route_name='view_gallery', renderer='view_gallery.mako')
def view_gallery(context, request):
    #one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    username = request.matchdict['username']
    print 'username:', username
    user = DBSession.query(UserModel).\
        filter(UserModel.name == username).\
        first()
    albums = user.albums
    #albums = DBSession.query(AlbumModel).join(UserModel).\
    #    filter(AlbumModel.user_id == UserModel.id).\
    #    filter(UserModel.name == username).\
    #    all()
    pictures = DBSession.query(PictureModel).all()

    def album_href(album):
        href = request.route_url('view_album',
                                 #username=username,
                                 album_name=album.name,
                                 **request.matchdict)
        return href

    return {'menu_urls' : create_menu_urls(context, request),
            'username' : username,
            'albums' : albums,
            'album_href' : album_href}

@view_config(route_name='view_album', renderer='view_album.mako')
def view_album(context, request):
    username, album_name = request.matchdict['username'], request.matchdict['album_name']
    user = DBSession.query(UserModel).\
        filter(UserModel.name == username).\
        first()
    album = user.albums[album_name]
    #album = DBSession.query(AlbumModel).join(UserModel).\
    #    filter(AlbumModel.name == album_name).\
    #    filter(AlbumModel.user_id == UserModel.id).\
    #    filter(UserModel.name == username).\
    #    first()
    pictures = album.pictures
    #pictures = DBSession.query(PictureModel).\
    #    filter(PictureModel.album_id == album.id).\
    #    all()
    def picture_href(picture):
        href = request.route_url('view_picture',
                                 #username=username,
                                 #album_name=album_name,
                                 picture_name=picture.name,
                                 **request.matchdict)
        return href

    return {'menu_urls' : create_menu_urls(context, request),
            'username' : username,
            'album' : album,
            'pictures' : pictures,
            'picture_href' : picture_href}

@view_config(route_name='view_picture', renderer='view_picture.mako')
def view_picture(context, request):
    username, album_name, picture_name = \
        request.matchdict['username'], \
        request.matchdict['album_name'], \
        request.matchdict['picture_name'],
    user = DBSession.query(UserModel).\
        filter(UserModel.name == username).\
        first()
    album = user.albums[album_name]
    picture = album.pictures[picture_name]
    #album = DBSession.query(AlbumModel).join(UserModel).\
    #    filter(AlbumModel.name == album_name).\
    #    filter(AlbumModel.user_id == UserModel.id).\
    #    filter(UserModel.name == username).\
    #    first()
    #picture = DBSession.query(PictureModel).\
    #    filter(PictureModel.name == picture_name).\
    #    filter(PictureModel.album_id == album.id).\
    #    first()

    def original_url(picture):
        #url = request.route_url('view_picture',
        #                         #username=username,
        #                         #album_name=album_name,
        #                         picture_name=picture.name,
        #                         **request.matchdict)
        url = picture.original_file
        return url
    def display_url(picture):
        url = picture.display_file
        return url
    def thumbnail_url(picture):
        url = picture.thumbnail_file
        return url

    return {'menu_urls' : create_menu_urls(context, request),
            'username' : username,
            'album' : album,
            'picture' : picture,
            'original_url' : original_url,
            'display_url' : display_url,
            'thumbnail_url' : thumbnail_url}
