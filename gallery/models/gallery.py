import datetime

from . import *

class AlbumModel(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    user_id = Column(None, ForeignKey("users.id"))
    description = Column(Text)
    location = Column(Text)
    date = Column(DateTime)

    user = relationship(
        "UserModel",
        backref=backref(
            'albums',
            collection_class=attribute_mapped_collection('name'),
            cascade='all, delete-orphan')
    )

    #user = user = relationship("UserModel")
    #user = relationship("UserModel", backref=backref("albums", order_by=id))

    #pictures = relationship(
        #"PictureModel",
        #collection_class=attribute_mapped_collection('name'),
        #cascade='all, delete-orphan',
        #backref='album'
    #)

    def __init__(self, name, description=None, location=None,
                 date_from=datetime.datetime.now(), date_to=None,
                 user_id=None):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.location = location
        self.date_from = date_from
        self.date_to = date_to

class PictureModel(Base):
    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True)
    display_file = Column(Text)
    original_file = Column(Text)
    thumbnail_file = Column(Text)
    name = Column(Text)
    description = Column(Text)
    album_id = Column(None, ForeignKey("albums.id"))
    location = Column(Text)
    date = Column(DateTime)

    album = relationship(
        "AlbumModel",
        backref=backref(
            'pictures',
            collection_class=attribute_mapped_collection('name'),
            cascade='all, delete-orphan')
    )

    #album = relationship("AlbumModel", backref=backref("pictures", order_by=id))

    def __init__(self, name, display_file, original_file=None, thumbnail_file=None,
                 description=None, location=None,
                 date=datetime.datetime.now(), album_id=None):
        self.name = name
        self.display_file = display_file
        self.original_file = original_file
        self.thumbnail_file = thumbnail_file
        self.description = description
        self.location = location
        self.date = date
        self.album_id = album_id
