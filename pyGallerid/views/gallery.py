import os
import datetime
import json
import urllib

from pyramid.location import lineage
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)
from pyramid.response import Response
from pyramid.traversal import find_resource

from ..models.user import User
from ..models.gallery import Gallery, GalleryContainer, GalleryAlbum, GalleryPicture


def picture_item(method):
    def new_method(item):
        if isinstance(item, GalleryContainer):
            item = item.preview_picture
        return method(item)
    return new_method
def picture_request_item(method):
    def new_method(request, item):
        if isinstance(item, GalleryContainer):
            item = item.preview_picture
        return method(request, item)
    return new_method

@picture_request_item
def original_url(request, item):
    file = item.original_file
    url = request.static_url(
        os.path.join(
            request.registry.settings['original_picture_dir'],
            item.original_file
        )
    )
    url = urllib.unquote(url)
    return url
@picture_item
def original_width(item):
    return item.original_width
@picture_item
def original_height(item):
    return item.original_height
@picture_request_item
def display_url(request, item):
    file = item.display_file
    url = request.static_url(
        os.path.join(
            request.registry.settings['display_picture_dir'],
            item.display_file
        )
    )
    url = urllib.unquote(url)
    return url
@picture_item
def display_width(item):
    return item.display_width
@picture_item
def display_height(item):
    return item.display_height
@picture_request_item
def thumbnail_url(request, item):
    file = item.thumbnail_file
    url = request.static_url(
        os.path.join(
            request.registry.settings['thumbnail_picture_dir'],
            item.thumbnail_file
        )
    )
    url = urllib.unquote(url)
    return url
@picture_item
def thumbnail_width(item):
    return item.thumbnail_width
@picture_item
def thumbnail_height(item):
    return item.thumbnail_height


@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=order-list')
def update_gallery_order_list(context, request):
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    pg_ids = json.loads(request.params['pg-value'])
    children = pg_context.children
    new_children = []
    for pg_id in pg_ids:
        new_children.append(children[pg_id])
    pg_context.children = new_children
    result['pg-status'] = 'success'
    result['pg-redirect-url'] = request.resource_url(context, '@@edit')
    #result['pg-redirect-url'] = request.resource_url(context)
    #result['pg-replace-url'] = request.resource_url(context)
    return result

@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=select-picture')
def update_gallery_select_picture(context, request):
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    pg_resource = find_resource(
        pg_context,
        json.loads(request.params['pg-value'])
    )
    print 'selected picture %s' % pg_resource.name
    pg_context.preview_picture = pg_resource
    result['pg-status'] = 'success'
    result['pg-redirect-url'] = request.resource_url(context, '@@edit')
    #result['pg-redirect-url'] = request.resource_url(context)
    #result['pg-replace-url'] = request.resource_url(context)
    return result


@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=attribute-multiline-text')
@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=attribute-text')
def update_gallery_attribute_text(context, request):
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    pg_name = request.params['pg-name']
    pg_text = json.loads(request.params['pg-value'])
    pg_context.__setattr__(pg_name, pg_text)
    if pg_context == context and pg_name == 'name':
        result['pg-redirect-url'] = request.resource_url(context, '@@edit')
        #result['pg-replace-url'] = request.resource_url(context)
    result['pg-status'] = 'success'
    return result

@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=attribute-date')
def update_gallery_attribute_date(context, request):
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    pg_name = request.params['pg-name']
    pg_value = json.loads(request.params['pg-value'])
    pg_date = datetime.datetime.strptime(pg_value, '%Y-%m-%d').date()
    pg_context.__setattr__(pg_name, pg_date)
    result['pg-date'] = '%d %s %d' % (date.day, date.strftime('%B'), date.year)    
    result['pg-status'] = 'success'
    return result

@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json',
             request_param='pg-type=attribute-date-from-to')
def update_gallery_attribute_date_from_to(context, request):
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    pg_name = request.params['pg-name']
    pg_value = json.loads(request.params['pg-value'])
    date_from, date_to = [
        datetime.datetime.strptime(date, '%Y-%m-%d').date() \
        for date in (pg_value['from'], pg_value['to'])
    ]
    if date_to < date_from:
        raise AssertionError('date_to < date_from')
    if pg_name == '__date_from_to':
        pg_context.date_from = date_from
        pg_context.date_to = date_to
    else:
        pg_context.__setattr__(pg_name, (date_from, date_to))
    date_str = '%d' % date_from.day
    if date_from.month != date_to.month:
        date_str += ' %s' % date_from.strftime('%B')
    if date_from.year != date_to.year:
        date_str += ' %d' % date_from.year
    date_str += ' - %d %s %d' % (date_to.day, date_to.strftime('%B'), date_to.year)
    result['pg-date-from-to'] = date_str
    result['pg-status'] = 'success'
    return result

#@view_config(context=GalleryContainer, xhr=True, name='update', renderer='json')
#def update_gallery(context, request):
    #result = {'pg-status' : 'failed'}
    #print request.params
    #print 'JSON request with id=%s, name=%s' % (request.params['pg-id'], request.params['pg-name'])
    #pg_id = request.params['pg-id']
    #pg_name = request.params['pg-name']
    #pg_id = pg_id.split(':')
    #if pg_id[0] in ('Gallery', 'GalleryContainer', 'Album') \
       #and pg_id[1] == '':
        #if pg_name in ['date_from', 'date_to']:
            #date = datetime.datetime.strptime(
                #request.params['pg-value'], '%Y-%m-%d').date()
            #result['pg-date'] = '%d %s %d' % (date.day, date.strftime('%B'), date.year)
        #if pg_name == '__date_from_to':
            #date_from = datetime.datetime.strptime(
                #request.params['pg-value[from]'], '%Y-%m-%d').date()
            #date_to = datetime.datetime.strptime(
                #request.params['pg-value[to]'], '%Y-%m-%d').date()
            #if date_to < date_from:
                #raise AssertionError('date_to < date_from')
            #context.date_to = date_to
            #context.date_from = date_from
            #date_s = '%d' % date_from.day
            #if date_from.month != date_to.month:
                #date_s += ' %s' % date_from.strftime('%B')
            #if date_from.year != date_to.year:
                #date_s += ' %d' % date_from.year
            #date_s += ' - %d %s %d' % (date_to.day, date_to.strftime('%B'), date_to.year)
            #result['pg-date-from-to'] = date_s
        #else:
            #context.__setattr__(pg_name, request.params['pg-value'])
        #result['pg-status'] = 'success'
        #return result
    #else:
        #if pg_id[1] in context:
            #context[pg_id[1]].__setattr__(pg_name, request.params['pg-value'])
            #result['pg-status'] = 'success'
            #return result
    #return result

@view_config(context=GalleryContainer, xhr=True, name='retrieve', renderer='json',
             request_param='pg-type=thumbnails')
def retrieve_thumbnails(context, request):
    result = {'pg-status' : 'failed'}
    pg_context = find_resource(context, request.params['pg-context'])
    children = pg_context.children
    pg_thumbnails = []
    for index, child in enumerate(children):
        if isinstance(child, GalleryContainer):
            thumbnail = child.preview_picture
        elif isinstance(child, GalleryPicture):
            thumbnail = child
        else:
            raise Exception("Can't retrieve thumbnails for this kind of object")
        pg_thumbnails.append({
            'index': index,
            'name': child.name,
            'url': thumbnail_url(request, thumbnail),
            'width': thumbnail_width(thumbnail),
            'height': thumbnail_height(thumbnail),
        })
    result['pg-thumbnails'] = json.dumps(pg_thumbnails)
    result['pg-status'] = 'success'
    return result

@view_config(context=GalleryContainer, name='edit',
             renderer='view_gallery.html.mako')
def view_gallery_edit(context, request):
    d = view_gallery(context, request)
    if request.registry.settings.get('allow_editing', 'false') == 'true':
        d.update({'editing' : True})
    return d

@view_config(context=GalleryContainer, renderer='view_gallery.html.mako')
def view_gallery(context, request):
    items = list(enumerate(context.children_iter))

    local_preview_url = lambda item: thumbnail_url(request, item.preview_picture)
    local_preview_width = lambda item: 0.5 * thumbnail_width(item.preview_picture)
    local_preview_height = lambda item: 0.5 * thumbnail_height(item.preview_picture)

    return {'gallery' : context,
            'items' : items,
            'editing' : False,
            'lineage_list' : list(lineage(context)),
            'preview_url' : local_preview_url,
            'preview_width' : local_preview_width,
            'preview_height' : local_preview_height}

@view_config(context=GalleryAlbum, name='edit',
             renderer='view_album.html.mako')
def view_album_edit(context, request):
    d = view_album(context, request)
    if request.registry.settings.get('allow_editing', 'false') == 'true':
        d.update({'editing' : True})
    return d

@view_config(context=GalleryAlbum, renderer='view_album.html.mako')
def view_album(context, request):
    display_mode = request.params.get('display_mode', 'list')
    if display_mode == 'list':
        pictures_per_page = 10
    elif display_mode == 'grid':
        pictures_per_page = 20
    else:
        pictures_per_page = -1
    if pictures_per_page > 0:
        num_of_pages = len(context) / pictures_per_page + 1
        try:
            page = int(request.params.get('page', 1))
        except ValueError:
            page = 1
        if page < 1 or page > num_of_pages:
            page = 1
        pictures_start_index = (page - 1) * pictures_per_page
        pictures_end_index = pictures_start_index + pictures_per_page
    else:
        page = 1
        num_of_pages = 1
        pictures_start_index = 0
        pictures_end_index = len(context.pictures)
    pictures = context.pictures[pictures_start_index:pictures_end_index]
    pictures = zip(
        xrange(pictures_start_index, pictures_end_index),
        pictures
    )

    local_original_url = lambda item: original_url(request, item)
    local_display_url = lambda item: display_url(request, item)
    if display_mode == 'list':
        local_preview_url = lambda item: display_url(request, item)
        local_preview_width = lambda item: display_width(item)
        local_preview_height = lambda item: display_height(item)
    else:
        local_preview_url = lambda item: thumbnail_url(request, item)
        local_preview_width = lambda item: thumbnail_width(item)
        local_preview_height = lambda item: thumbnail_height(item)

    return {'album' : context,
            'editing' : False,
            'lineage_list' : list(lineage(context)),
            'pictures' : pictures,
            'display_mode' : display_mode,
            'page' : page,
            'num_of_pages' : num_of_pages,
            'original_url' : local_original_url,
            'display_url' : local_display_url,
            'preview_url' : local_preview_url,
            'preview_width' : local_preview_width,
            'preview_height' : local_preview_height}
