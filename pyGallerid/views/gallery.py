import os
import datetime

from pyramid.location import lineage
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)
from pyramid.response import Response

from ..models.user import User
from ..models.gallery import Gallery, GalleryContainer, GalleryAlbum, GalleryPicture

@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json')
def update_gallery(context, request):
    result = {'pg-status' : 'failed'}
    print request.params
    print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    pg_id = request.params['pg-id']
    pg_name = request.params['pg-name']
    pg_id = pg_id.split(':')
    if pg_id[0] in ('Gallery', 'GalleryContainer', 'Album') \
       and pg_id[1] == '':
        if pg_name in ['date_from', 'date_to']:
            date = datetime.datetime.strptime(
                request.params['pg-value'], '%Y-%m-%d').date()
            result['pg-date'] = '%d %s %d' % (date.day, date.strftime('%B'), date.year)
        if pg_name == '__date_from_to':
            date_from = datetime.datetime.strptime(
                request.params['pg-value[from]'], '%Y-%m-%d').date()
            date_to = datetime.datetime.strptime(
                request.params['pg-value[to]'], '%Y-%m-%d').date()
            if date_to < date_from:
                raise AssertionError('date_to < date_from')
            context.date_to = date_to
            context.date_from = date_from
            date_s = '%d' % date_from.day
            if date_from.month != date_to.month:
                date_s += ' %s' % date_from.strftime('%B')
            if date_from.year != date_to.year:
                date_s += ' %d' % date_from.year
            date_s += ' - %d %s %d' % (date_to.day, date_to.strftime('%B'), date_to.year)
            result['pg-date-from-to'] = date_s
        else:
            context.__setattr__(pg_name, request.params['pg-value'])
        result['pg-status'] = 'success'
        return result
    else:
        if pg_id[1] in context:
            context[pg_id[1]].__setattr__(pg_name, request.params['pg-value'])
            result['pg-status'] = 'success'
            return result
    return result

@view_config(context=GalleryContainer, name='edit',
             renderer='view_gallery.html.mako')
def view_gallery_edit(context, request):
    d = view_gallery(context, request)
    d.update({'editing' : True})
    return d

@view_config(context=GalleryContainer, renderer='view_gallery.html.mako')
def view_gallery(context, request):
    preview_type = 'thumbnail'
    def preview_url(category):
        picture = category.preview_picture
        file = picture.thumbnail_file
        url = request.static_url(
            os.path.join(
                request.registry.settings['%s_picture_dir' % preview_type],
                picture.thumbnail_file
            )
        )
        return url
    def preview_width(category):
        picture = category.preview_picture
        return int(0.5 * picture.__getattribute__('%s_width' % preview_type))
    def preview_height(category):
        picture = category.preview_picture
        return int(0.5 * picture.__getattribute__('%s_height' % preview_type))

    return {'gallery_container' : context,
            'editing' : False,
            'lineage_list' : list(lineage(context)),
            'preview_url' : preview_url,
            'preview_width' : preview_width,
            'preview_height' : preview_height}

@view_config(context=GalleryAlbum, name='edit',
             renderer='view_album.html.mako')
def view_album_edit(context, request):
    d = view_album(context, request)
    d.update({'editing' : True})
    return d

@view_config(context=GalleryAlbum, renderer='view_album.html.mako')
def view_album(context, request):
    if request.params.get('grid', 'False') == 'True':
        pictures_per_page = 20
    else:
        pictures_per_page = 10
    num_of_pages = len(context) / pictures_per_page + 1
    try:
        page = int(request.params.get('page', 1))
    except ValueError:
        page = 1
    if page < 1 or page > num_of_pages:
        page = 1
    pictures_start_index = (page - 1) * pictures_per_page
    pictures_end_index = pictures_start_index + pictures_per_page
    pictures = context.pictures[pictures_start_index:pictures_end_index]

    #def original_url(picture):
        #file = picture.original_file
        #url = request.static_url(
            #os.path.join(
                #request.registry.settings['original_picture_dir'],
                #picture.original_file
            #)
        #)
        #return url
    def display_url(picture):
        file = picture.display_file
        url = request.static_url(
            os.path.join(
                request.registry.settings['display_picture_dir'],
                picture.display_file
            )
        )
        return url
    preview_type = 'display'
    if request.params.get('grid', 'False') == 'True':
        preview_type = 'thumbnail'
    def preview_url(picture):
        file = picture.thumbnail_file
        url = request.static_url(
            os.path.join(
                request.registry.settings['%s_picture_dir' % preview_type],
                picture.thumbnail_file
            )
        )
        return url
    def preview_width(picture):
        return picture.__getattribute__('%s_width' % preview_type)
    def preview_height(picture):
        return picture.__getattribute__('%s_height' % preview_type)

    return {'album' : context,
            'editing' : False,
            'lineage_list' : list(lineage(context)),
            'pictures' : pictures,
            'show_as_grid' : request.params.get('grid', 'False'),
            'page' : page,
            'num_of_pages' : num_of_pages,
            #'original_url' : original_url,
            'display_url' : display_url,
            'preview_url' : preview_url,
            'preview_width' : preview_width,
            'preview_height' : preview_height}
