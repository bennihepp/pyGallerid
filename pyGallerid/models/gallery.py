import datetime

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList


class PersistentLocationAware(object):
    __name__ = None
    __parent__ = None

    @property
    def name(self):
        return self.__name__

    @name.setter
    def name(self, value):
        print 'setting name of', self, 'to', value
        if self.parent is not None:
            print 'changing linkage to parent object'
            parent = self.parent
            del parent[self.name]
            self.__name__ = value
            parent[value] = self
            print 'self.parent[name] =', self.parent[self.name]
        else:
            raise AttributeError('The name of a root object can\'t be changed')

    @property
    def parent(self):
        return self.__parent__


class GalleryContainer(PersistentDict, PersistentLocationAware):
    def __init__(self, name, description=None, parent=None):
        PersistentDict.__init__(self)
        PersistentLocationAware.__init__(self)
        self.__name__ = name
        self.__parent__ = parent
        if description is None:
            self.description = name
        else:
            self.description = description
        self.preview_picture = None
        self.preview_size = (-1, -1)
        self.__children = PersistentList()

    @property
    def children_iter(self):
        return self.__children.__iter__()

    @property
    def children(self):
        return list(self.__children)

    @children.setter
    def children(self, children):
        if len(children) != len(self):
            raise ValueError('len(children) and len(self) must be equal')
        for child in children:
            if not child.name in self:
                raise ValueError('children and self must ' \
                                 'contain the same objects')
        self.__children = PersistentList(children)

    def add(self, item):
        self[item.__name__] = item
        item.__parent__ = self

    def insert(self, index, item):
        self.add(item)
        self.__children.insert(index, item)

    def __setitem__(self, name, item):
        if item.__name__ != name:
            raise ValueError('name and item.__name__ must be equal')
        PersistentDict.__setitem__(self, name, item)
        item.__parent__ = self
        self.__children.append(item)

    def __delitem__(self, name):
        self.__children.remove(self[name])
        self[name].__parent__ = None
        PersistentDict.__delitem__(self, name)

    def __iter__(self):
        return self.values().__iter__()


class Gallery(GalleryContainer):
    def __init__(self, description=None, user=None, parent=None):
        GalleryContainer.__init__(self, None, description, parent)
        self.user = user


class GalleryAlbum(GalleryContainer):
    def __init__(self, name, album_path, description=None, \
                 long_description=None, location=None, \
                 date_from=datetime.datetime.now(), date_to=None,
                 parent=None):
        GalleryContainer.__init__(self, name, description, parent=parent)
        self.__album_path = album_path
        self.long_description = long_description
        self.location = location
        self.date_from = date_from
        self.date_to = date_to

    @property
    def album_path(self):
        return self.__album_path

    @album_path.setter
    def album_path(self, path):
        # TODO: implement
        self._album_path = path

    pictures_iter = property(lambda self: self.children_iter)
    pictures = property(lambda self: self.children)

    @pictures.setter
    def pictures(self, pictures):
        self.children = pictures


class GalleryPicture(Persistent, PersistentLocationAware):
    def __init__(self, name, big_image_view, regular_image_view,
                 small_image_view, description=None, location=None,
                 date=datetime.datetime.now(), parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self)
        self.__name__ = name
        self.__parent__ = parent
        if isinstance(big_image_view, GalleryImage):
            self.big_image_view = GalleryImageView(big_image_view)
        else:
            self.big_image_view = big_image_view
        if isinstance(regular_image_view, GalleryImage):
            self.regular_image_view = GalleryImageView(regular_image_view)
        else:
            self.regular_image_view = regular_image_view
        if isinstance(small_image_view, GalleryImage):
            self.small_image_view = GalleryImageView(small_image_view)
        else:
            self.small_image_view = small_image_view
        self.description = description
        self.location = location
        self.date = date


class GalleryImageView(Persistent):
    def __init__(self, image, view_size=None, crop_rect=None):
        self.image = image
        self.view_size = view_size
        self.crop_rect = crop_rect

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
    def __init__(self, image_file, image_size=(-1, -1), tags=None):
        self.image_file = image_file
        self.image_size = image_size
        self.tags = tags

    @property
    def width(self):
        return self.image_size[0]

    @property
    def height(self):
        return self.image_size[1]

    def __contains__(self, tag):
        return tag in self.tags

    def __getitem__(self, tag):
        return self.tags[tag]
