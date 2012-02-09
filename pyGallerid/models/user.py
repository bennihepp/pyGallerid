# -*- coding: utf-8 -*-

"""
Provides models for the user resources of pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import random
import hashlib
import string

from pyramid.traversal import find_root
from pyramid.security import Everyone, Allow

from . import PersistentContainer

HASHCLASS = hashlib.sha512
HASHSIZE = 2 * HASHCLASS().digest_size
SALTSIZE = HASHSIZE


class User(PersistentContainer):
    __attributes__ = ['email', 'password_hash', 'password_salt']

    def __init__(self, name, email, password, parent=None):
        PersistentContainer.__init__(self, name, parent)
        self.email = email
        self.change_password(password)
        self.__acl__ = [
            (Allow, Everyone, 'view'),
            (Allow, Everyone, 'login'),
            (Allow, name, 'logout'),
            (Allow, name, 'edit'),
            (Allow, name, 'update'),
            (Allow, name, 'remove'),
        ]

    def authenticate(self, password):
        hexhash = HASHCLASS(password + self.password_salt)
        return hexhash.hexdigest() == self.password_hash

    def change_password(self, password):
        self.password_hash, self.password_salt = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        password_salt = ''.join(
            random.choice(string.printable) for x in xrange(SALTSIZE)
        )
        hexhash = HASHCLASS(password + password_salt)
        return hexhash.hexdigest(), password_salt


def groupfinder(username, request):
    root = find_root(request.context)
    if username in root:
        return username
    else:
        #raise KeyError('Unknown user: %s' % username)
        return None
