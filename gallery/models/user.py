import random
import hashlib
import string

from persistent import Persistent

HASHCLASS = hashlib.sha512
HASHSIZE = 2 * HASHCLASS().digest_size
SALTSIZE = HASHSIZE

class User(Persistent):
    def __init__(self, name, email, password_hash, password_salt, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.email = email
        self.password_hash = password_hash
        self.password_salt = password_salt

    @property
    def name(self):
        return self.__name__

    def authenticate(self, password):
        hexhash = HASHCLASS(password, self.password_salt)
        return hexhash.hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password):
        password_salt = ''.join(random.choice(string.printable) for x in xrange(SALTSIZE))
        hexhash = HASHCLASS(password + password_salt)
        return hexhash.hexdigest(), password_salt
