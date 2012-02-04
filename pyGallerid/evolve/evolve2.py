# -*- coding: utf-8 -*-

"""
repoze.evolution script for the pyGallerid database.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


from pyramid.security import Everyone, Allow

from . import walk_resources

from ..models.user import User


def evolve(context):
    for resource in walk_resources(context):
        if isinstance(resource, User):
            if not hasattr(resource, '__acl__'):
                name = resource.name
                resource.__acl__ = [
                    (Allow, Everyone, 'view'),
                    (Allow, Everyone, 'login'),
                    (Allow, Everyone, 'logout'),
                    (Allow, name, 'edit'),
                    (Allow, name, 'update'),
                ]
