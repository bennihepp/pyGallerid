# -*- coding: utf-8 -*-

"""
repoze.evolution script for the pyGallerid database.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


from . import walk_resources

def evolve(context):
    for resource in walk_resources(context):
        cls = type(resource)
        if hasattr(cls, '__attributes__') \
           and not hasattr(resource, '__attributes__'):
            resource.__attributes__ = cls.__attributes__
