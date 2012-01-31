# -*- coding: utf-8 -*-

"""
repoze.evolution package for the pyGallerid database.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


from collections import deque

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList

def walk_resources(root):
    dq = deque()
    dq.append(root)
    while len(dq) > 0:
        resource = dq.popleft()
        if isinstance(resource, Persistent):
            yield resource
        if isinstance(resource, PersistentDict):
            for name in resource:
                dq.append(resource[name])
        elif isinstance(resource, PersistentList):
            for child in resource:
                dq.append(child)
