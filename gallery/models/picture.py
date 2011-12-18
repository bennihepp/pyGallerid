from . import *

class PictureModel(Base):
    __tablename__ = 'pictures'
    id = Column(Integer, primary_key=True)
    display_url = Column(Text)
    original_url = Column(Text)
    thumbnail_url = Column(Text)
    name = Column(Text)
    description = Column(Text)
    album_id = Column(None, ForeignKey("albums.id"))
    #location = Column(Text)
    #date = Column(DateTime)

    def __init__(self, display_url, original_url=None, thumbnail_url=None,
                 name=None, description=None, album_id=None):
        self.display_url = display_url
        self.original_url = original_url
        self.thumbnail_url = thumbnail_url
        self.name = name
        self.description = description
        self.album_id = album_id
        #self.location = location
        #self.date = date

