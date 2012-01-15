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
        if self.parent is not None:
            self.parent[value] = self
            del self.parent[self.name]
            self.__name__ = value
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
        self.preview_size = (-1,-1)
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
                raise ValueError('children and self must contain the same objects')
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
    def __init__(self, name, description=None, long_description=None,
                 location=None,
                 date_from=datetime.datetime.now(), date_to=None,
                 parent=None):
        GalleryContainer.__init__(self, name, description, parent=parent)
        self.long_description = long_description
        self.location = location
        self.date_from = date_from
        self.date_to = date_to

    pictures_iter = property(lambda self: self.children_iter)
    pictures = property(lambda self: self.children)
    @pictures.setter
    def pictures(self, pictures):
        self.children = pictures

class GalleryPicture(Persistent, PersistentLocationAware):
    def __init__(self, name,
                 display_file, original_file=None, thumbnail_file=None,
                 description=None,
                 location=None,
                 date=datetime.datetime.now(),
                 original_size=(-1, -1),
                 display_size=(-1, -1),
                 thumbnail_size=(-1, -1),
                 parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self)
        self.__name__ = name
        self.__parent__ = parent
        self.display_file = display_file
        self.original_file = original_file
        self.thumbnail_file = thumbnail_file
        self.description = description
        self.location = location
        self.date = date
        self.original_width = original_size[0]
        self.original_height = original_size[1]
        self.display_width = display_size[0]
        self.display_height = display_size[1]
        self.thumbnail_width = thumbnail_size[0]
        self.thumbnail_height = thumbnail_size[1]
