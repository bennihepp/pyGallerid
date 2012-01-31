# -*- coding: utf-8 -*-

"""
Provides common models and helpers for resources of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


from persistent.dict import PersistentDict
from persistent.list import PersistentList

__sw_version__ = 1


class PersistentLocationAware(object):
    __name__ = None
    __parent__ = None

    def __init__(self, name, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        if parent is not None:
            parent[name] = self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.__name__

    @name.setter
    def name(self, value):
        if self.parent is not None:
            p = self.parent
            self.parent = None
            #del parent[self.name]
            self.__name__ = value
            self.parent = p
            #p[value] = self
        else:
            raise AttributeError('The name of a root object can\'t be changed')

    @property
    def parent(self):
        return self.__parent__

    @parent.setter
    def parent(self, obj):
        if self.parent is not None:
            p = self.parent
            self.__parent__ = None
            del p[self.name]
        if obj is not None:
            obj[self.name] = self
            self.__parent__ = obj


class PersistentContainer(PersistentDict, PersistentLocationAware):
    def __init__(self, name, parent=None):
        PersistentDict.__init__(self)
        PersistentLocationAware.__init__(self, name, parent)
        self.__name__ = name
        if parent is not None:
            parent[name] = self
        self.__parent__ = parent

    def __add(self, item):
        PersistentDict.__setitem__(self, item.__name__, item)
        item.__parent__ = self
    add = __add

    def __setitem__(self, name, item):
        if item.__name__ != name:
            raise ValueError('name and item.__name__ must be equal')
        self.__add(item)

    def __delitem__(self, name):
        self[name].__parent__ = None
        PersistentDict.__delitem__(self, name)


class PersistentOrderedContainer(PersistentContainer):
    def __init__(self, name, parent=None):
        PersistentContainer.__init__(self, name, parent)
        self.__children = PersistentList()

    def index(self, item):
        return self.__children.index(item)

    def get_children(self, index):
        return self.__children[index]

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
        if item.__name__ not in self:
            self.__children.append(item)
        else:
            raise ValueError('The container already contains this item')
        PersistentContainer.add(self, item)
    append = add

    def insert(self, index, item):
        if item.__name__ not in self:
            self.__children.insert(index, item)
        else:
            raise ValueError('The container already contains this item')
        PersistentContainer.append(self, item)

    def __setitem__(self, name, item):
        already_in_children = name in self
        PersistentContainer.__setitem__(self, name, item)
        if not already_in_children:
            self.__children.append(item)

    def __delitem__(self, name):
        if name in self:
            self.__children.remove(self[name])
        PersistentContainer.__delitem__(self, name)

    def __iter__(self):
        return self.iterkeys()

    def keys(self):
        return [child.name for child in self.__children]

    def values(self):
        return [child for child in self.__children]

    def items(self):
        return [(child.name, child) for child in self.__children]

    def iterkeys(self):
        for child in self.__children:
            yield child.name

    def itervalues(self):
        for child in self.__children:
            yield child

    def iteritems(self):
        for child in self.__children:
            yield child.name, child


def retrieve_user(app, username):
    if username in app:
        return app[username]
    else:
        return None


def retrieve_gallery(user):
    if 'gallery' in user:
        return user['gallery']
    return None


def retrieve_about(user):
    if 'about' in user:
        return user['about']
    return None


def bootstrap_db():
    return PersistentContainer('', None)


def appmaker(zodb_root):
    if not 'pyGallerid-app-root' in zodb_root:
        app_root = bootstrap_db()
        zodb_root['pyGallerid-app-root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['pyGallerid-app-root']
