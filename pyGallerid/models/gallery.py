# -*- coding: utf-8 -*-

"""
Provides models for the gallery resources of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os
import shutil
import datetime

from persistent import Persistent

from . import PersistentLocationAware, PersistentOrderedContainer


class GalleryDocument(Persistent, PersistentLocationAware):
    __attributes__ = ('description', 'long_description')

    def __init__(self, name, description, long_description, parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self, name, parent)
        self.description = description
        self.long_description = long_description


class GalleryContainer(PersistentOrderedContainer):
    __attributes__ = ('path', 'absolute_path', 'description',
                       'preview_picture', 'preview_size')

    def __init__(self, name, description=None, preview_picture=None,
                 path=None, parent=None):
        PersistentOrderedContainer.__init__(self, name, parent)
        if description is None:
            self.description = name
        else:
            self.description = description
        self.__preview_picture = None
        self.preview_size = (-1, -1)
        self.__path = path

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, new_path):
        if self.__path is not None:
            try:
                abs_path_tuple = self.absolute_path_tuple
                abs_parent_path = os.path.join(*abs_path_tuple[:-1])
                old_abs_path = os.path.join(abs_parent_path, self.path)
                new_abs_path = os.path.join(abs_parent_path, new_path)
                if os.path.exists(new_abs_path):
                    if os.path.isdir(new_abs_path):
                        for file in os.listdir(old_abs_path):
                            shutil.move(os.path.join(old_abs_path, file),
                                        new_abs_path)
                        os.rmdir(old_abs_path)
                    else:
                        raise ValueError('The new path already exists'
                                         ' and is not a directory')
                else:
                    shutil.move(old_abs_path, new_abs_path)
            except OSError, shutil.Error:
                print 'Unable to change path of gallery container:', self.name
                raise
        self.__path = new_path

    @property
    def absolute_path(self):
        if self.path is None:
            raise AttributeError('The container has no valid path')
        if isinstance(self.parent, GalleryContainer):
            return os.path.join(self.parent.absolute_path, self.path)
        else:
            return self.path

    @property
    def absolute_path_tuple(self):
        if self.path is None:
            raise AttributeError('The container has no valid path')
        if isinstance(self.parent, GalleryContainer):
            return self.parent.absolute_path_tuple + (self.path,)
        else:
            return (self.path,)

    @property
    def preview_picture(self):
        if self.__preview_picture is None and len(self) > 0:
            child = self.get_children(0)
            if isinstance(child, GalleryPicture):
                return child
            else:
                return child.preview_picture
        else:
            return self.__preview_picture

    @preview_picture.setter
    def preview_picture(self, picture):
        assert isinstance(picture, GalleryPicture) \
               or isinstance(picture, GalleryContainer)
        if isinstance(picture, GalleryContainer):
            picture = picture.preview_picture
        if self.has_picture(picture):
            self.__preview_picture = picture
        else:
            raise ValueError("The container must contain it's "
                             "own preview picture")

    def has_picture(self, picture):
        assert isinstance(picture, GalleryPicture)
        found = False
        for child in self.itervalues():
            if isinstance(child, GalleryContainer):
                if child.has_picture(picture):
                    found = True
                    break
            elif isinstance(child, GalleryPicture):
                if picture == child:
                    found = True
                    break
        return found


class Gallery(GalleryContainer):
    __attributes__ = ['user']
    __attributes__.extend(GalleryContainer.__attributes__)

    def __init__(self, description=None, path=None,
                 user=None, name='gallery', parent=None):
        GalleryContainer.__init__(self, name, description,
                                  path=path, parent=parent)
        self.user = user


class GalleryAlbum(GalleryContainer):
    __attributes__ = ['long_description', 'location', 'date_from', 'date_to']
    __attributes__.extend(GalleryContainer.__attributes__)

    def __init__(self, name, description=None, \
                 long_description=None, location=None, \
                 date_from=datetime.datetime.now(), date_to=None,
                 path=None, parent=None):
        GalleryContainer.__init__(self, name, description,
                                  path=path, parent=parent)
        self.long_description = long_description
        self.location = location
        self.date_from = date_from
        self.date_to = date_to

    pictures = property(lambda self: self.children)

    @pictures.setter
    def pictures(self, pictures):
        self.children = pictures


class GalleryPicture(Persistent, PersistentLocationAware):
    __attributes__ = ['big_image_view', 'regular_image_view',
                      'small_image_view', 'description', 'location',
                      'date']

    def __init__(self, name, big_image_view, regular_image_view,
                 small_image_view, description=None, location=None,
                 date=datetime.datetime.now(), parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self, name, parent)
        if isinstance(big_image_view, GalleryImageFile):
            self.big_image_view = GalleryImageView(big_image_view)
        else:
            assert isinstance(big_image_view, GalleryImageView)
            self.big_image_view = big_image_view
        if isinstance(regular_image_view, GalleryImageFile):
            self.regular_image_view = GalleryImageView(regular_image_view)
        else:
            assert isinstance(regular_image_view, GalleryImageView)
            self.regular_image_view = regular_image_view
        if isinstance(small_image_view, GalleryImageFile):
            self.small_image_view = GalleryImageView(small_image_view)
        else:
            assert isinstance(small_image_view, GalleryImageView)
            self.small_image_view = small_image_view
        self.description = description
        self.location = location
        self.date = date

    @property
    def small_image_path(self):
        assert self.parent is not None
        assert isinstance(self.parent, GalleryAlbum)
        return os.path.join(self.parent.absolute_path,
                            self.small_image_view.image.filename)

    @property
    def regular_image_path(self):
        assert self.parent is not None
        assert isinstance(self.parent, GalleryAlbum)
        return os.path.join(self.parent.absolute_path,
                            self.regular_image_view.image.filename)

    @property
    def big_image_path(self):
        assert self.parent is not None
        assert isinstance(self.parent, GalleryAlbum)
        return os.path.join(self.parent.absolute_path,
                            self.big_image_view.image.filename)


class GalleryImageView(Persistent):
    def __init__(self, image, view_size=None, crop_rect=None):
        self.image = image
        self.view_size = view_size
        self.crop_rect = crop_rect

    def __str__(self):
        return self.image.filename

    @property
    def width(self):
        if self.view_size is None:
            return self.image.width
        return self.view_size[0]

    @property
    def height(self):
        if self.view_size is None:
            return self.image.height
        return self.view_size[1]

    @property
    def crop_x(self):
        if self.crop_rect is None:
            return 0
        return self.crop_rect[0]

    @property
    def crop_y(self):
        if self.crop_rect is None:
            return 0
        return self.crop_rect[1]

    @property
    def crop_width(self):
        if self.crop_rect is None:
            return self.width
        return self.crop_rect[2] - self.crop_rect[0]

    @property
    def crop_height(self):
        if self.crop_rect is None:
            return self.height
        return self.crop_rect[3] - self.crop_rect[1]


class GalleryImageFile(Persistent):
    def __init__(self, filename, size=(-1, -1), tags=None):
        self.filename = filename
        self.size = size
        self.tags = tags

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def __contains__(self, tag):
        return tag in self.tags

    def __getitem__(self, tag):
        return self.tags[tag]
