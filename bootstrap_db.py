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

email = sys.argv[1]
config = sys.argv[2]
password = sys.argv[3]
path = sys.argv[4]

resource_path = ''

subprocess.call(['bin/init_gallery', config, email, password])

try:
    subprocess.check_call([
        'bin/import_pictures', config, resource_path, path
    ])
except subprocess.CalledProcessError:
    print 'Unable to import pictures:', path
    raise

