# -*- coding: utf-8 -*-

"""
Provides views for the gallery resources of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import datetime
import json
import urllib
import itertools
import logging
import os
import math
from abc import ABCMeta, abstractmethod
from zope.interface.interface import InterfaceClass

from pyramid.location import lineage
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
)
from pyramid.traversal import find_resource, find_root, find_interface, \
     resource_path
from pyramid.security import authenticated_userid, remember, forget

from persistent.dict import PersistentDict
from persistent.list import PersistentList

from ..models import retrieve_about, retrieve_gallery, retrieve_user
from ..models.user import User
from ..models.gallery import GalleryResource, GalleryContainer, \
     GalleryAlbum, GalleryPicture, GalleryDocument

from . import ViewHandler

logger = logging.getLogger(__name__)


#from pyramid.events import subscriber, NewRequest
#@subscriber(NewRequest)
#def newRequestSubscriber(event):
    #request = event.request
    #pass


def picture_item(method):
    def new_method(item):
        if isinstance(item, GalleryContainer):
            item = item.preview_picture
        #if item is None:
            #return ""
        return method(item)
    return new_method


def picture_request_item(method):
    def new_method(self, item):
        if isinstance(item, GalleryContainer):
            item = item.preview_picture
        #if item is None:
            #return ""
        return method(self, item)
    return new_method


class GalleryHandlerMixin(object):

    @picture_request_item
    def big_url(self, item):
        url = self.request.static_url(item.big_image_path)
        url = urllib.unquote(url)
        return url

    @staticmethod
    @picture_item
    def big_width(item):
        return item.big_image_view.width

    @staticmethod
    @picture_item
    def big_height(item):
        return item.big_image_view.height

    @picture_request_item
    def regular_url(self, item):
        url = self.request.static_url(item.regular_image_path)
        url = urllib.unquote(url)
        return url

    @staticmethod
    @picture_item
    def regular_width(item):
        return item.regular_image_view.width

    @staticmethod
    @picture_item
    def regular_height(item):
        return item.regular_image_view.height

    @picture_request_item
    def small_url(self, item):
        url = self.request.static_url(item.small_image_path)
        url = urllib.unquote(url)
        return url

    @staticmethod
    @picture_item
    def small_width(item):
        return item.small_image_view.width

    @staticmethod
    @picture_item
    def small_height(item):
        return item.small_image_view.height

    @staticmethod
    def render_resource(resource):
        name = resource.name
        name = name[0].upper() + name[1:]
        return unicode(name)

    @staticmethod
    def find_gallery_resource(resource):
        user = itertools.ifilter(
            lambda r: isinstance(r, User), lineage(resource)
        ).next()
        return retrieve_gallery(user)

    @staticmethod
    def find_about_resource(resource):
        user = itertools.ifilter(
            lambda r: isinstance(r, User), lineage(resource)
        ).next()
        return retrieve_about(user)

    @classmethod
    def remove_resource_files_recursive(cls, resource):
        if isinstance(resource, GalleryAlbum):
            for child in resource:
                if isinstance(child, GalleryPicture):
                    for path in (child.big_image_path,
                                 child.regular_image_path,
                                 child.small_image_path):
                        os.remove(path)
        # the elif is really important here,
        # because GalleryAlbum inherits from GalleryContainer
        elif isinstance(resource, GalleryContainer):
            for child in resource.itervalues():
                cls.remove_resource_files_recursive(child)

    @classmethod
    def remove_resource_files(cls, resource):
        try:
            cls.remove_resource_files_recursive(resource)
        except OSError as exc:
            import traceback
            logging.warn('Error while removing files: ' \
                         + traceback.format_exc())
            raise


class GalleryHandler(ViewHandler, GalleryHandlerMixin):

    __metaclass__ = ABCMeta

    def __init__(self, context, request):
        super(GalleryHandler, self).__init__(context, request)
        tpl_context = {}
        tpl_context['lineage_list'] = list(lineage(context))[:-2]
        tpl_context['messages'] = request.session.pop_flash()
        tpl_context['user'] = request.user
        tpl_context['editing'] = False
        tpl_context['allow_editing'] = self.allow_editing()
        tpl_context['about_url'] = self.about_url()
        tpl_context['render_resource'] = self.render_resource
        self.tpl_context = tpl_context

    @abstractmethod
    def edit(self):
        tpl_context = self.view()
        tpl_context['editing'] = True
        return tpl_context

    @abstractmethod
    def view(self):
        return self.tpl_context

    def allow_editing(self):
        user = find_interface(self.context, User)
        if user is not None \
           and authenticated_userid(self.request) == user.name:
            return True
        else:
            return False

    def about_url(self):
        about_resource = self.find_about_resource(self.context)
        if about_resource != self.context:
            about_url = self.request.resource_url(
                about_resource, '@@' + self.request.view_name)
        else:
            about_url = None
        return about_url


def context_pred(context_type, return_as_tuple=True):
    def context_pred_interface(context, request):
        return context_type.providedBy(context)
    def context_pred_class(context, request):
        return isinstance(context, context_type)
    if isinstance(context_type, InterfaceClass):
        pred = context_pred_interface
    else:
        pred = context_pred_class
    if return_as_tuple:
        return (pred,)
    else:
        return pred


@view_defaults(context=GalleryResource, xhr=True, name='remove',
               renderer='json', permission='remove')
class GalleryXHRRemoveHandler(ViewHandler, GalleryHandlerMixin):

    @view_config()
    def remove_item(self):
        context, request = self.context, self.request
        result = {'pg-status': 'failed'}
        pg_context = find_resource(context, request.params['pg-context'])
        # TODO: introduce acl for removal control into models
        if pg_context == retrieve_about(request.user):
            return result
        elif pg_context == retrieve_gallery(request.user):
            return result
        pg_context.parent = None
        self.remove_resource_files(pg_context)
        request.session.flash('Item "%s" removed.' % pg_context.name)
        result['pg-redirect-url'] = request.resource_url(context, '@@edit')
        result['pg-status'] = 'success'
        return result


@view_defaults(context=GalleryResource, xhr=True, name='update',
               renderer='json', permission='update')
class GalleryXHRUpdateHandler(ViewHandler, GalleryHandlerMixin):

    @view_config(request_param='pg-type=attribute-multiline-text')
    @view_config(request_param='pg-type=attribute-text')
    def update_gallery_attribute_text(self):
        context, request = self.context, self.request
        #print 'JSON request with id=%s, name=%s' \
              #% (request.params['pg-id'], request.params['pg-name'])
        result = {'pg-status': 'failed'}
        pg_context = find_resource(context, request.params['pg-context'])
        pg_name = request.params['pg-name']
        pg_text = json.loads(request.params['pg-value'])
        if self.find_gallery_resource(pg_context) == pg_context \
           and pg_name == 'name':
            logger.info('Attempt to change name of gallery resource: %s' \
                        % pg_context)
            return result
        if self.find_about_resource(pg_context) == pg_context \
           and pg_name == 'name':
            logger.info('Attempt to change name of about resource: %s' \
                        % pg_context)
            return result
        pg_context.__setattr__(pg_name, pg_text)
        if pg_context == context and pg_name == 'name':
            result['pg-redirect-url'] = request.resource_url(context, '@@edit')
            #result['pg-replace-url'] = request.resource_url(context)
        result['pg-status'] = 'success'
        return result

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=attribute-date')
    def update_gallery_attribute_date(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        #print 'JSON request with id=%s, name=%s' \
              #% (request.params['pg-id'], request.params['pg-name'])
        result = {'pg-status': 'failed'}
        pg_context = find_resource(context, request.params['pg-context'])
        pg_name = request.params['pg-name']
        pg_value = json.loads(request.params['pg-value'])
        date = datetime.datetime.strptime(pg_value, '%Y-%m-%d').date()
        pg_context.__setattr__(pg_name, date)
        result['pg-date'] = '%d %s %d' \
            % (date.day, date.strftime('%B'), date.year)
        result['pg-status'] = 'success'
        return result

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=attribute-date-from-to')
    def update_gallery_attribute_date_from_to(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        #print 'JSON request with id=%s, name=%s' \
              #% (request.params['pg-id'], request.params['pg-name'])
        result = {'pg-status': 'failed'}
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
        date_str += ' - %d %s %d' % (date_to.day, date_to.strftime('%B'),
                                     date_to.year)
        result['pg-date-from-to'] = date_str
        result['pg-status'] = 'success'
        return result

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=order-list')
    def update_gallery_order_list(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        # TODO: implement CSRF
        #token = request.session.get_csrf_token()
        #if request.params['pg-csrf'] != token:
            #raise ValueError('CSRF token did not match!')
        #print 'JSON request with id=%s, name=%s' \
              #% (request.params['pg-id'], request.params['pg-name'])
        result = {'pg-status': 'failed'}
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

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=select-picture')
    def update_gallery_select_picture(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        #print 'JSON request with id=%s, name=%s' \
              #% (request.params['pg-id'], request.params['pg-name'])
        result = {'pg-status': 'failed'}
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


@view_defaults(context=GalleryResource, xhr=True, name='retrieve',
               renderer='json', permission='view')
class GalleryXHRRetrieveHandler(ViewHandler, GalleryHandlerMixin):

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=pictures')
    def retrieve_pictures(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        result = {'pg-status': 'failed'}
        pg_context = find_resource(context, request.params['pg-context'])
        if 'pg-slice' in request.params:
            pg_slice = [int(x) for x in request.params['pg-slice'].split(':')]
            pg_slice = slice(*pg_slice)
        else:
            pg_slice = slice(None)
        indices = range(len(pg_context))[pg_slice]
        pg_pictures = []
        for index, child in enumerate(pg_context.itervalues()):
            if index not in indices:
                continue
            if isinstance(child, GalleryContainer):
                thumbnail = child.preview_picture
            elif isinstance(child, GalleryPicture):
                thumbnail = child
            else:
                raise Exception("Can't retrieve thumbnails "
                                "for this kind of object")
            pg_pictures.append({
                'index': index,
                'name': child.name,
                'big_url': self.big_url(thumbnail),
                'regular_url': self.regular_url(thumbnail),
                'width': self.regular_width(thumbnail),
                'height': self.regular_height(thumbnail),
            })
        result['pg-pictures'] = json.dumps(pg_pictures)
        result['pg-status'] = 'success'
        return result

    @view_config(custom_predicates=context_pred(GalleryContainer),
                 request_param='pg-type=thumbnails',
                 permission='view')
    def retrieve_thumbnails(self):
        context, request = self.context, self.request
        assert isinstance(context, GalleryContainer)
        result = {'pg-status': 'failed'}
        pg_context = find_resource(context, request.params['pg-context'])
        pg_thumbnails = []
        for index, child in enumerate(pg_context.itervalues()):
            if isinstance(child, GalleryContainer):
                thumbnail = child.preview_picture
            elif isinstance(child, GalleryPicture):
                thumbnail = child
            else:
                raise Exception("Can't retrieve thumbnails "
                                "for this kind of object")
            pg_thumbnails.append({
                'index': index,
                'name': child.name,
                'url': self.small_url(thumbnail),
                'width': self.small_width(thumbnail),
                'height': self.small_height(thumbnail),
            })
        result['pg-thumbnails'] = json.dumps(pg_thumbnails)
        result['pg-status'] = 'success'
        return result

    @staticmethod
    def convert_resource_to_json(resource, state='closed'):
        json_resource = {}
        json_resource['state'] = state
        if resource == find_root(resource):
            json_resource['data'] = '<root>'
        else:
            json_resource['data'] = str(resource)
        json_resource['attr'] = {'pg-path': resource_path(resource)}
        metadata = {}
        if hasattr(resource, '__attributes__'):
            for attr_name in resource.__attributes__:
                metadata[attr_name] = str(getattr(resource, attr_name))
        json_resource['metadata'] = metadata
        if not isinstance(resource, PersistentDict) \
           and not isinstance(resource, PersistentList):
            del json_resource['state']
        return json_resource

    @classmethod
    def convert_lineage_to_json(cls, resource, descendants):
        json_resource = cls.convert_resource_to_json(
            resource, state='open')
        if isinstance(resource, PersistentDict):
            iterator = resource.itervalues()
        elif isinstance(resource, PersistentList):
            iterator = resource.__iter__()
        else:
            iterator = ().__iter__()
        children = []
        for child in iterator:
            if len(descendants) > 0 and child == descendants[0]:
                json_child = cls.convert_lineage_to_json(
                    child, descendants[1:])
            else:
                json_child = cls.convert_resource_to_json(
                    child, state='closed')
            children.append(json_child)
        json_resource['children'] = children
        return json_resource

    @view_config(request_param='pg-type=resource-lineage', permission='edit')
    def retrieve_resource_lineage(self):
        context, request = self.context, self.request
        result = {'pg-status': 'failed'}

        descendants = list(lineage(context))[::-1]
        root = descendants[0]
        pg_lineage = self.convert_lineage_to_json(root, descendants[1:])
        result['pg-data'] = json.dumps(pg_lineage)
        result['pg-status'] = 'success'
        return result

    @view_config(request_param='pg-type=resource-children', permission='edit')
    def retrieve_resource_children(self):
        context, request = self.context, self.request
        result = {'pg-status': 'failed'}
        resource = find_resource(find_root(context), request.params['pg-path'])
        if isinstance(resource, PersistentDict):
            pg_children = [ \
                self.convert_resource_to_json(child) \
                    for child in resource.itervalues()
            ]
        elif isinstance(resource, PersistentList):
            pg_children = [ \
                self.convert_resource_to_json(child) \
                    for child in resource
            ]
        else:
            pg_children = []
        result['pg-data'] = json.dumps(pg_children)
        result['pg-status'] = 'success'
        return result


@view_defaults(context=GalleryResource)
class GalleryAuthHandler(ViewHandler):

    @view_config(name='login', permission='login')
    def login(self):
        context, request = self.context, self.request
        username = request.params['username']
        password = request.params['password']
        root = find_root(context)
        user = retrieve_user(root, username)
        if user is not None and user.authenticate(password):
            headers = remember(request, username)
            request.session.flash('Logged in successfully')
        else:
            headers = None
            request.session.flash('Login failed')
        #resp = render_view_to_response(context)
        #return resp
        url = request.resource_url(context)
        return HTTPFound(location=url, headers=headers)
        #response = view_gallery(context, request)
        #response.headers.update(hreaders)
        #return response

    @view_config(name='logout', permission='logout')
    def logout(self):
        context, request = self.context, self.request
        headers = forget(request)
        request.session.flash('Logged out')
        #resp = render_view_to_response(context)
        #return resp
        url = request.resource_url(context)
        return HTTPFound(location=url, headers=headers)


@view_defaults(context=GalleryContainer, renderer='view_container.html.mako')
class GalleryContainerHandler(GalleryHandler):

    def __init__(self, context, request):
        super(GalleryContainerHandler, self).__init__(context, request)
        self.init_container()

    def init_container(self):
        context, request = self.context, self.request

        # TODO: do something else about empty containers
        items = []
        for item in context.itervalues():
            if len(item) > 0:
                items.append(item)
            #else:
                #print 'empty album:', item.name
        items = list(enumerate(items))
        #items = list(enumerate(context))

        self.tpl_context['gallery'] = context
        self.tpl_context['items'] = items
        self.tpl_context['small_url'] = self.small_url
        self.tpl_context['small_width'] = self.small_width
        self.tpl_context['small_height'] = self.small_height

    @view_config(name='edit', permission='edit')
    def edit(self):
        return super(GalleryContainerHandler, self).edit()

    @view_config(permission='view')
    def view(self):
        return super(GalleryContainerHandler, self).view()


@view_defaults(context=GalleryAlbum, renderer='view_album.html.mako')
class GalleryAlbumHandler(GalleryHandler):

    def __init__(self, context, request):
        super(GalleryAlbumHandler, self).__init__(context, request)
        self.init_album()

    def init_album(self):
        context, request = self.context, self.request

        display_mode = request.params.get('display_mode', 'list')
        if display_mode == 'list':
            pictures_per_page = 10
        elif display_mode == 'grid':
            pictures_per_page = 20
        else:
            pictures_per_page = -1
        if pictures_per_page > 0:
            num_of_pages = math.ceil(len(context) / float(pictures_per_page))
            num_of_pages = int(num_of_pages)
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

        self.tpl_context['album'] = context
        self.tpl_context['pictures'] = pictures
        self.tpl_context['display_mode'] = display_mode
        self.tpl_context['page'] = page
        self.tpl_context['num_of_pages'] = num_of_pages
        self.tpl_context['total_num_of_pictures'] = len(context)
        self.tpl_context['small_url'] = self.small_url
        self.tpl_context['small_width'] = self.small_width
        self.tpl_context['small_height'] = self.small_height
        self.tpl_context['regular_url'] = self.regular_url
        self.tpl_context['regular_width'] = self.regular_width
        self.tpl_context['regular_height'] = self.regular_height
        self.tpl_context['big_url'] = self.big_url

    @view_config(name='edit', permission='edit')
    def edit(self):
        return super(GalleryAlbumHandler, self).edit()

    @view_config(permission='view')
    def view(self):
        return super(GalleryAlbumHandler, self).view()


@view_defaults(context=GalleryDocument, renderer='view_document.html.mako')
class GalleryDocumentHandler(GalleryHandler):

    def __init__(self, context, request):
        super(GalleryDocumentHandler, self).__init__(context, request)
        self.tpl_context['document'] = context
        self.tpl_context['lineage_list'] = \
            [context, self.find_gallery_resource(context)]

    @view_config(name='edit', permission='edit')
    def edit(self):
        return super(GalleryDocumentHandler, self).edit()

    @view_config(permission='view')
    def view(self):
        return super(GalleryDocumentHandler, self).view()
