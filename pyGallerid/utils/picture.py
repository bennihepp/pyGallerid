# -*- coding: utf-8 -*-

"""
Provides helpers for handling and importing image files.
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp


import os
import re
import dateutil.parser
import subprocess
import shutil
import Image
from ExifTags import TAGS

from ..models.gallery import GalleryContainer, GalleryAlbum, \
     GalleryPicture, GalleryImageFile

DEFAULT_MIN_THUMBNAIL_SIZE = 400
DEFAULT_DISPLAY_SCALE = 0.5

MAX_REGULAR_VIEW_WIDTH = 1024
MAX_REGULAR_VIEW_HEIGHT = 536

MAX_SMALL_VIEW_WIDTH = 300
MAX_SMALL_VIEW_HEIGHT = 300


def open_picture(filename, return_tags=True):
    img = Image.open(filename)
    if return_tags:
        #from ExifTags import TAGS
        info = img._getexif()
        tags = {}
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            tags[decoded] = value
    else:
        tags = None
    return img, tags


def get_scaled_size(width, height, max_width, max_height):
    scale = max_width / float(width)
    if round(height * scale) > max_height:
        scale = max_height / float(height)
    width = int(round(width * scale))
    height = int(round(height * scale))
    return (width, height)


def create_gallery_image_file(filename, tags=None):
    img, new_tags = open_picture(filename, return_tags=(tags is None))
    if tags is None:
        tags = new_tags
    width, height = img.size
    image = GalleryImageFile(
        filename,
        size=(width, height),
        tags=tags
    )
    return image


def create_regular_gallery_image_file(filename, output_filename,
                                      width, height, tags,
                                      use_image_magick=True):
    new_size = get_scaled_size(
        width, height,
        MAX_REGULAR_VIEW_WIDTH, MAX_REGULAR_VIEW_HEIGHT)
    if use_image_magick:
        try:
            subprocess.check_call(['convert', filename, '-resize',
                                   '%dx%d!' % new_size,
                                   output_filename])
        except subprocess.CalledProcessError as e:
            print 'ImageMagick failed with errorcode %d' % e.returncode
            print '\n'.join(['  %s' % line for line in '\n'.split(e.output)])
            raise
    else:
        img = Image.open(filename)
        img = img.resize(new_size, Image.ANTIALIAS)
        img.save(output_filename)
    return create_gallery_image_file(output_filename, tags)


def create_small_gallery_image_file(filename, output_filename,
                                    width, height, tags,
                                    use_image_magick=True):
    new_size = get_scaled_size(
        width, height,
        MAX_SMALL_VIEW_WIDTH, MAX_SMALL_VIEW_HEIGHT)
    if use_image_magick:
        try:
            subprocess.check_call(['convert', filename, '-resize',
                                   '%dx%d!' % new_size,
                                   output_filename])
        except subprocess.CalledProcessError as e:
            print 'ImageMagick failed with errorcode %d' % e.returncode
            print '\n'.join(['  %s' % line for line in '\n'.split(e.output)])
            raise
    else:
        img = Image.open(filename)
        img = img.resize(new_size, Image.ANTIALIAS)
        img.save(output_filename)
    return create_gallery_image_file(output_filename, tags)


def import_gallery_picture(original_filename, big_filename, regular_filename,
                           small_filename, default_date=None, move_file=True,
                           use_image_magick=True):

    if os.path.abspath(original_filename) != os.path.abspath(big_filename):
        if move_file:
            shutil.move(original_filename, big_filename)
        else:
            shutil.copy2(original_filename, big_filename)

    img, tags = open_picture(big_filename)

    big_image = create_gallery_image_file(big_filename, tags)
    width, height = big_image.width, big_image.height

    regular_image = create_regular_gallery_image_file(
        big_filename, regular_filename, width, height, use_image_magick)
    small_image = create_small_gallery_image_file(
        big_filename, small_filename, width, height, use_image_magick)

    dates = []
    for tag in ('DateTime', 'DateTimeOriginal', 'DateTimeDigitized'):
        if tag in tags:
            dates.append(dateutil.parser.parse(tags[tag]))
    if len(dates) > 0:
        date = min(dates)
    else:
        if default_date is None:
            raise ValueError('No date found for:', original_filename)
        else:
            logging.warning('No date found: %s' % original_filename)
            date = default_date

    name = os.path.splitext(os.path.basename(original_filename))[0]
    description = name
    location = None

    picture = GalleryPicture(name, big_image, regular_image, small_image,
                             description, location, date)

    return picture


def import_gallery_album(album_path, settings, move_files=True,
                         use_image_magick=True, sorting_order='number'):

    rel_album_path = os.path.basename(album_path)

    datematcher = re.compile(
        r'^([\d]{4}) ([a-zA-Z0-9]{1,9}) ([\d]{1,2})(?:\-([\d]{1,2}))? (.+)$')
    try:
        mo = datematcher.match(rel_album_path)
        year, month, day_from, day_to, album_name = mo.groups()
        date_from = dateutil.parser.parse(
            '%s %s %s' % (year, month, day_from)).date()
        date_to = dateutil.parser.parse(
            '%s %s %s' % (year, month, day_to)).date()
        print '  album date: from %s to %s' % (date_from, date_to)
    except (AttributeError, ValueError):
        logging.warning('Unable to extract dates: %s' % rel_album_path)
        raise

    big_image_dir = os.path.join(settings['image_dir'], album_path, 'big')
    regular_image_dir = os.path.join(
        settings['image_dir'], album_path, 'regular')
    small_image_dir = os.path.join(settings['image_dir'], album_path, 'small')
    for path in (big_image_dir, regular_image_dir, small_image_dir):
        if not os.path.exists(path):
            os.makedirs(path)

    print 'scanning %s' % album_path
    pictures = []
    for filename in os.listdir('.'):
        if filename.startswith('.'):
            continue
        filebase, fileext = os.path.splitext(filename)
        if os.path.isfile(filename) and fileext.lower() in \
            ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            print '  importing %s' % filename
            big_filename = os.path.join(big_image_dir, filename)
            regular_filename = os.path.join(regular_image_dir, filename)
            small_filename = os.path.join(small_image_dir, filename)
            try:
                picture = import_gallery_picture(
                    filename, big_filename,
                    regular_filename, small_filename,
                    move_file=move_files)
            except:
                print 'Failed to import picture:', \
                      os.path.join(album_path, filename)
                raise
            pictures.append(picture)

    if len(pictures) == 0:
        return None

    album = GalleryAlbum(album_name, album_name, album_name,
                         None, date_from, date_to, rel_album_path)
    if sorting_order == 'date':
        pictures.sort(cmp=lambda x, y: cmp(x.date, y.date))
    elif sorting_order == 'number':
        pattern = re.compile('(.+?)([0-9]+).*?')

        def match_picture(picture):
            mo = pattern.match(picture.name)
            return mo.group(1), int(mo.group(2))

        def cmp_pictures(picture1, picture2):
            prefix1, num1 = match_picture(picture1)
            prefix2, num2 = match_picture(picture2)
            if cmp(prefix1, prefix2) != 0:
                return cmp(prefix1, prefix2)
            else:
                return cmp(num1, num2)
        pictures.sort(cmp=cmp_pictures)
    else:
        pictures.sort(cmp=lambda x, y: cmp(x.name, y.name))

    for picture in pictures:
        # make image file paths relative
        for image, image_dir in ( \
            (picture.big_image_view.image, big_image_dir),
            (picture.regular_image_view.image, regular_image_dir),
            (picture.small_image_view.image, small_image_dir),
        ):
            head, tail = os.path.split(image.filename)
            head2, tail2 = os.path.split(head)
            image.filename = os.path.join(tail2, tail)
        # add picture to album container
        album.append(picture)

    return album


def import_gallery_container(path, settings, move_files=True,
                             use_image_magick=True, sorting_order='number'):
    cwd = os.getcwd()
    os.chdir(os.path.split(path)[-1])
    album = None
    containers = []
    picture_found = False
    print 'scanning %s' % path
    for filename in os.listdir('.'):
        if filename.startswith('.'):
            continue
        container = None
        filebase, fileext = os.path.splitext(filename)
        if not picture_found and os.path.isfile(filename) \
           and fileext.lower() in \
           ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            try:
                album = import_gallery_album(
                    path, settings, move_files, use_image_magick)
            except:
                print 'Failed to import album:', path
                raise
            picture_found = True
        elif os.path.isdir(filename):
            abs_path = os.path.join(path, filename)
            try:
                container = import_gallery_container(
                    abs_path, settings, move_files,
                    use_image_magick, sorting_order)
            except:
                print 'Failed to import container:', abs_path
                raise
            if container is not None:
                containers.append(container)
    os.chdir(cwd)
    if len(containers) > 0:
        if album is None:
            rel_path = os.path.basename(path)
            new_container = GalleryContainer(
                rel_path, rel_path, None, rel_path)
        else:
            new_container = album
        [new_container.add(c) for c in containers]
        return new_container
    elif album is not None:
        return album
