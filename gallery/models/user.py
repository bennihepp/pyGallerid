import random
import hashlib
import string

from . import *

HASHCLASS = hashlib.sha512
HASHSIZE = 2 * HASHCLASS().digest_size
SALTSIZE = HASHSIZE

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    email = Column(Text)
    password_hash = Column(Text(HASHSIZE))
    password_salt = Column(Text(SALTSIZE))

    #albums = relationship(
    #    "AlbumModel",
    #    collection_class=attribute_mapped_collection('name'),
    #    cascade='all, delete-orphan',
    #    backref='user'
    #)

    def __init__(self, name, email, password_hash, password_salt):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.password_salt = password_salt

    def authenticate(self, password):
        hexhash = HASHCLASS(password, self.password_salt)
        return hexhash.hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password):
        password_salt = ''.join(random.choice(string.printable) for x in xrange(SALTSIZE))
        hexhash = HASHCLASS(password + password_salt)
        return hexhash.hexdigest(), password_salt
