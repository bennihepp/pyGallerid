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

    #user = relationship("UserModel", backref=backref("albums", order_by=id))

    def __init__(self, name, user_id=None, description=None, location=None,
                 date=datetime.datetime.now()):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.location = location
        self.date = date

