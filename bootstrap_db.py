# -*- coding: utf-8 -*-

"""
Script for bootstrapping the pyGallerid database.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


#!/bin/env python

import os
import sys
import subprocess

username = 'hepp'
email = 'benjamin.hepp@gmail.com'
config = sys.argv[1]
password = sys.argv[2]
path = sys.argv[3]

subprocess.call(['bin/init_gallery', config, username, email, password])

try:
    subprocess.check_call([
        'bin/import_pictures', config, username, path
    ])
except subprocess.CalledProcessError:
    print 'Unable to import pictures:', path
    raise

