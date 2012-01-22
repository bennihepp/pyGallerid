import datetime

from persistent import Persistent

from . import PersistentLocationAware, PersistentOrderedContainer


class GalleryDocument(Persistent, PersistentLocationAware):
    def __init__(self, name, description, long_description, parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self, name, parent)
        self.description = description
        self.long_description = long_description


class GalleryContainer(PersistentOrderedContainer):
    def __init__(self, name, description=None,
                 preview_picture=None, parent=None):
        PersistentOrderedContainer.__init__(self, name, parent)
        if description is None:
            self.description = name
        else:
            self.description = description
        self.__preview_picture = None
        self.preview_size = (-1, -1)

    @property
    def preview_picture(self):
        if self.__preview_picture is None and len(self) > 0:
            child = self.get_children(0)
            if isinstance(child, GalleryPicture):
                return child
            else:
                return child.preview_picture
        else:
            return self.__preview_picture

    @preview_picture.setter
    def preview_picture(self, picture):
        if self.has_picture(picture):
            self.__preview_picture = picture
        else:
            raise ValueError("The container must contain it's "
                             "own preview picture")

    def has_picture(self, picture):
        found = False
        for child in self:
            if isinstance(child, GalleryContainer):
                if child.has_picture(picture):
                    found = True
                    break
            elif isinstance(child, GalleryPicture):
                if picture == child:
                    found = True
                    break
        return found


class Gallery(GalleryContainer):
    def __init__(self, description=None,
                 user=None, name='gallery', parent=None):
        GalleryContainer.__init__(self, name, description, parent)
        self.user = user


class GalleryAlbum(GalleryContainer):
    def __init__(self, name, description=None, \
                 long_description=None, location=None, \
                 date_from=datetime.datetime.now(), date_to=None,
                 parent=None):
        GalleryContainer.__init__(self, name, description, parent=parent)
        #self.__album_path = album_path
        self.long_description = long_description
        self.location = location
        self.date_from = date_from
        self.date_to = date_to

    #@property
    #def album_path(self):
        #return self.__album_path

    #@album_path.setter
    #def album_path(self, path):
        ## TODO: implement
        #self._album_path = path

    pictures = property(lambda self: self.children)

    @pictures.setter
    def pictures(self, pictures):
        self.children = pictures


class GalleryPicture(Persistent, PersistentLocationAware):
    def __init__(self, name, big_image_view, regular_image_view,
                 small_image_view, description=None, location=None,
                 date=datetime.datetime.now(), parent=None):
        Persistent.__init__(self)
        PersistentLocationAware.__init__(self, name, parent)
        if isinstance(big_image_view, GalleryImageFile):
            self.big_image_view = GalleryImageView(big_image_view)
        else:
            self.big_image_view = big_image_view
        if isinstance(regular_image_view, GalleryImageFile):
            self.regular_image_view = GalleryImageView(regular_image_view)
        else:
            self.regular_image_view = regular_image_view
        if isinstance(small_image_view, GalleryImageFile):
            self.small_image_view = GalleryImageView(small_image_view)
        else:
            self.small_image_view = small_image_view
        self.description = description
        self.location = location
        self.date = date


class GalleryImageView(Persistent):
    def __init__(self, image, view_size=None, crop_rect=None):
        self.image = image
        self.view_size = view_size
        self.crop_rect = crop_rect

    @property
    def width(self):
        if self.view_size is None:
            return self.image.width
        return self.view_size[0]

    @property
    def height(self):
        if self.view_size is None:
            return self.image.height
        return self.view_size[1]

    @property
    def crop_x(self):
        if self.crop_rect is None:
            return 0
        return self.crop_rect[0]

    @property
    def crop_y(self):
        if self.crop_rect is None:
            return 0
        return self.crop_rect[1]

    @property
    def crop_width(self):
        if self.crop_rect is None:
            return self.width
        return self.crop_rect[2] - self.crop_rect[0]

    @property
    def crop_height(self):
        if self.crop_rect is None:
            return self.height
        return self.crop_rect[3] - self.crop_rect[1]


class GalleryImageFile(Persistent):
    def __init__(self, image_file, image_size=(-1, -1), tags=None):
        self.image_file = image_file
        self.image_size = image_size
        self.tags = tags

    @property
    def width(self):
        return self.image_size[0]

    @property
    def height(self):
        return self.image_size[1]

    def __contains__(self, tag):
        return tag in self.tags

    def __getitem__(self, tag):
        return self.tags[tag]
