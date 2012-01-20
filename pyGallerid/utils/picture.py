import os
import sys
import re
import datetime
import dateutil.parser
import hashlib
import subprocess
import shutil
import Image
from ExifTags import TAGS

from ..models import appmaker
from ..models.user import User
from ..models.gallery import GalleryContainer, Gallery, GalleryAlbum, \
     GalleryPicture, GalleryImageView, GalleryImageFile

DEFAULT_MIN_THUMBNAIL_SIZE = 400
DEFAULT_DISPLAY_SCALE = 0.5
#MAX_DISPLAY_WIDTH = 1024
#MAX_DISPLAY_HEIGHT = 536


def open_picture(filename, return_tags=True):
    img = Image.open(filename)
    if return_tags:
        from ExifTags import TAGS
        info = img._getexif()
        tags = {}
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            tags[decoded] = value
    else:
        tags = None
    return img, tags


def create_gallery_image_file(filename, tags=None):
    img, new_tags = open_picture(filename, return_tags=(tags is None))
    if tags is None:
        tags = new_tags
    width, height = img.size
    image = GalleryImageFile(
        filename,
        image_size=(width, height),
        tags
    )
    return image


def create_regular_gallery_image_file(filename, output_filename,
                                      width, height, tags,
                                      use_image_magick=True):
    if use_image_magick:
        try:
            ret = subprocess.check_output(['convert', filename, '-resize',
                                   '%d%%' % round(100 * DEFAULT_DISPLAY_SCALE),
                                   output_filename])
        except subprocess.CalledProcessError as e:
            print 'ImageMagick failed with errorcode %d' % e.returncode
            print '\n'.join(['  %s' % line for line in '\n'.split(e.output)])
            raise
    else:
        new_width = round(DEFAULT_DISPLAY_SCALE * width)
        new_height = round(DEFAULT_DISPLAY_SCALE * height)
        img = Image.open(filename)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        img.save(output_filename)
    return create_gallery_image_file(output_filename, tags)


def create_small_gallery_image_file(filename, output_filename,
                                    width, height, tags,
                                    use_image_magick=True):
    aspect_ratio = float(width) / height
    if width < height:
        new_width = 400
        new_height = 400 / aspect_ratio
    else:
        new_height = 400
        new_width = 400 * aspect_ratio

    if use_image_magick:
        try:
            ret = subprocess.check_output(['convert', filename, '-resize',
                                   '%dx%d!' % (new_width, new_height),
                                   output_filename])
        except subprocess.CalledProcessError as e:
            print 'ImageMagick failed with errorcode %d' % e.returncode
            print '\n'.join(['  %s' % line for line in '\n'.split(e.output)])
            raise
    else:
        img = Image.open(filename)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        img.save(output_filename)
    return create_gallery_image_file(output_filename, tags)


def import_gallery_picture(original_filename, big_filename, regular_filename,
                           small_filename, default_date=None, move_file=False,
                           use_image_magick=True):

    if move_file:
        shutil.move(filename, big_filename
    else:
        shutil.copy2(filename, big_filename)

    img, tags = open_picture(big_filename)

    big_image = create_gallery_image_file(big_filename, tags)
    width, height = big_image.width, big_image.height

    regular_image = create_regular_gallery_image_file(
        big_filename, regular_filename, width, height, use_image_magick)
    small_image = create_small_gallery_image_file(
        big_filename, small_filename, width, height, use_image_magick)

    name = os.path.basename(filename)
    description = name

    picture = GalleryPicture(
        name, big_image, regular_image, small_image, description,
        location, date
    )

    if 'DateTimeOriginal' in tags:
        date = dateutil.parser.parse(tags['DateTimeOriginal'])
    elif 'DateTime' in tags:
        date = dateutil.parser.parse(tags['DateTime'])
    else:
        if default_date is not None:
            print 'WARNING: No date found!! Listing all tags:'
            for k,v in tags.items():
                print '  %s: %s' % (k, v)
            # TODO: handle this case
            import sys
            sys.exit(1)
            #date = datetime.datetime.now()
        date = default_date

    picture = GalleryPicture(name, big_image, regular_image, small_image,
                             description, None, date)


def import_gallery_album(root, move_files=False, use_image_magick=True):

    big_image_dir = settings['big_image_dir']
    regular_image_dir = settings['regular_image_dir']
    small_image_dir = settings['small_image_dir']

    # TODO: remove
    #files = os.listdir(albumpath)
    #files.sort()

    gallery_pictures = []

    album_datematcher = re.compile(
        r'^([\d]{4}) ([a-zA-Z0-9]{1,9}) ([\d]{1,2})(?:\-([\d]{1,2}))? (.+)$')

    print 'scanning %s' % root
    for file in os.listdir(root):
        arr = os.path.splitext(file)
        if len(arr) > 1:
            if arr[-1].lower() in \
                ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                print '  importing %s' % file
                album_path = os.path.relpath(albumpath, picture_dir)
                try:
                    match = datematcher.match(album_path)
                    year, month, day_from, day_to, album_name = match.groups()
                    print year, month, day_from
                    date_from = dateutil.parser.parse(
                        '%s %s %s' % (year, month, day_from)).date()
                    date_to = dateutil.parser.parse(
                        '%s %s %s' % (year, month, day_to)).date()
                except (AttributeError, ValueError):
                    album_name = album_path
                    date_from = None
                    date_to = None
                picture_name = arr[0]
                abs_file = os.path.join(root, file)
                original_file = os.path.relpath(abs_file, picture_dir)
                thumbnail_file = original_file
                abs_thumbnail_file = os.path.join(
                    thumbnail_dir,
                    original_file)
                display_file = original_file
                abs_display_file = os.path.join(
                    display_dir,
                    original_file)
                print '  generating thumbnail'
                img = Image.open(abs_file)
                from ExifTags import TAGS
                info = img._getexif()
                ret = {}
                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
                if 'DateTimeOriginal' in ret:
                    date = dateutil.parser.parse(ret['DateTimeOriginal'])
                elif 'DateTime' in ret:
                    date = dateutil.parser.parse(ret['DateTime'])
                else:
                    print 'WARNING: No date found!!'
                    for k,v in ret.items():
                        print k, ':', v
                    import sys
                    sys.exit(1)
                    date = None
                #print 'info:', img.info.keys()
                #
                thumb_img = img.copy()
                thumb_img.thumbnail(DEFAULT_THUMBNAIL_SIZE, Image.ANTIALIAS)
                if not os.path.exists(os.path.split(abs_thumbnail_file)[0]):
                    os.makedirs(os.path.split(abs_thumbnail_file)[0])
                thumb_img.save(abs_thumbnail_file)
                display_img = img.copy()
                img_width, img_height = img.size
                scale = MAX_DISPLAY_WIDTH / float(img_width)
                if scale * img_height > MAX_DISPLAY_HEIGHT:
                    scale = MAX_DISPLAY_HEIGHT / float(img_height)
                display_size = (int(scale * img_width),
                                int(scale * img_height))
                display_img.thumbnail(display_size, Image.ANTIALIAS)
                if not os.path.exists(os.path.split(abs_display_file)[0]):
                    os.makedirs(os.path.split(abs_display_file)[0])
                display_img.save(abs_display_file)
                import_picture(
                    category, album_name,
                    date_from, date_to,
                    picture_name,
                    original_file, display_file, thumbnail_file,
                    img.size, display_img.size, thumb_img.size,
                    date)
