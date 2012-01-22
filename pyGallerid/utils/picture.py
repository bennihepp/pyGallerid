import os
import re
import dateutil.parser
import subprocess
import shutil
import Image
from ExifTags import TAGS

from ..models.gallery import GalleryAlbum, GalleryPicture, GalleryImageFile

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
        image_size=(width, height),
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

    if original_filename != big_filename:
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

    if 'DateTimeOriginal' in tags:
        date = dateutil.parser.parse(tags['DateTimeOriginal'])
    elif 'DateTime' in tags:
        date = dateutil.parser.parse(tags['DateTime'])
    else:
        if default_date is not None:
            print 'WARNING: No date found:', original_filename
            print 'Listing all tags:'
            for k, v in tags.items():
                print '  %s: %s' % (k, v)
            # TODO: handle this case
            #date = datetime.datetime.now()
            raise
        date = default_date

    name = os.path.splitext(os.path.basename(original_filename))[0]
    description = name
    location = None

    picture = GalleryPicture(name, big_image, regular_image, small_image,
                             description, location, date)

    return picture


def import_gallery_album(album_path, settings, move_files=True,
                         use_image_magick=True):

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
        print 'WARNING: Unable to extract dates:', album_path
        # TODO
        #album_name = album_path
        #date_from = None
        #date_to = None
        raise

    big_image_dir = settings['big_image_dir']
    regular_image_dir = settings['regular_image_dir']
    small_image_dir = settings['small_image_dir']
    for directory in (big_image_dir, regular_image_dir, small_image_dir):
        path = os.path.join(directory, rel_album_path)
        if not os.path.exists(path):
            os.makedirs(path)

    print 'scanning %s' % album_path
    pictures = []
    for filename in os.listdir(album_path):
        picture_name, picture_ext = os.path.splitext(filename)
        if (not filename.startswith('.')) and picture_ext.lower() in \
            ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            print '  importing %s' % filename
            rel_filename = os.path.join(rel_album_path, filename)
            big_filename = os.path.join(big_image_dir, rel_filename)
            regular_filename = os.path.join(regular_image_dir, rel_filename)
            small_filename = os.path.join(small_image_dir, rel_filename)
            original_filename = os.path.join(album_path, filename)
            picture = import_gallery_picture(
                original_filename, big_filename,
                regular_filename, small_filename,
                move_file=move_files)
            pictures.append(picture)

    if len(pictures) == 0:
        return None

    album = GalleryAlbum(album_name, album_name, album_name,
                         None, date_from, date_to)
    pictures.sort(cmp=lambda x, y: cmp(x.date, y.date))
    for picture in pictures:
        # make image file paths relative
        for image, image_dir in ( \
            (picture.big_image_view.image, big_image_dir),
            (picture.regular_image_view.image, regular_image_dir),
            (picture.small_image_view.image, small_image_dir),
        ):
            path = image.image_file
            rel_path = os.path.relpath(path, image_dir)
            image.image_file = rel_path
        # add picture to album container
        album.append(picture)

    return album
