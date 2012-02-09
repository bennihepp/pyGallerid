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
readme = open(os.path.join(here, 'README.rst')).read()
changes = open(os.path.join(here, 'CHANGES.rst')).read()

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
    'pyramid_rewrite',
]

setup(name='pyGallerid',
    version='0.2',
    description='python web photo gallery based on pyramid',
    long_description=readme + '\n' +  changes,
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
    author='Benjamin Hepp',
    author_email='benjamin.hepp@gmail.com',
    license='BSD',
    url='https://github.com/bennihepp/pyGallerid',
    keywords='web pyramid pylons gallery photo',
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
    remove_pictures = pyGallerid.scripts.remove_pictures:main
    """,
)

