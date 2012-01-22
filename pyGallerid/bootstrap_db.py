#!/bin/env python

import os
import sys
import subprocess

username = 'hepp'
email = 'benjamin.hepp@gmail.com'
config = sys.argv[1]
password = sys.argv[2]

subprocess.call(['bin/init_gallery', config, username, email, password])

for category in os.listdir('data/pictures/original'):
    for album in os.listdir(os.path.join('data/pictures/original', category)):
        path = os.path.join('data/pictures/original', category, album)
        subprocess.check_call([
            'bin/import_album', config, username, category, path
        ])

