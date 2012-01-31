# -*- coding: utf-8 -*-

"""
Setuptools setup.py file for pyGallerid.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'pyramid_tm',
    'ZODB3',
    'pyramid_zodbconn',
    #'repoze.zodbconn',
    'transaction',
    'PIL',
    'python-dateutil==1.5',
    'repoze.evolution',
]

setup(name='pyGallerid',
      version='0.1',
      description='python web photo gallery based on pyramid',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons python gallery photo',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pyGallerid",
      entry_points = """\
      [paste.app_factory]
      main = pyGallerid:main
      [console_scripts]
      init_gallery = pyGallerid.scripts.init_gallery:main
      import_pictures = pyGallerid.scripts.import_pictures:main
      """,
      )

