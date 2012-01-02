from . import *

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    email = Column(Text)
    password_hash = Column(Text)

    #albums = relationship(
    #    "AlbumModel",
    #    collection_class=attribute_mapped_collection('name'),
    #    cascade='all, delete-orphan',
    #    backref='user'
    #)

    def __init__(self, name, email, password_hash):
        self.name = name
        self.email = email
        self.password_hash = password_hash
