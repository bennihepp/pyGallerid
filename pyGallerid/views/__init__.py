# -*- coding: utf-8 -*-

"""
Provides basic view classes for pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp

class ViewHandler(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
