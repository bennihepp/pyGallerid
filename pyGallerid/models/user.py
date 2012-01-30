import random
import hashlib
import string

from pyramid.traversal import find_root
from pyramid.security import Everyone, Allow

from . import PersistentContainer

HASHCLASS = hashlib.sha512
HASHSIZE = 2 * HASHCLASS().digest_size
SALTSIZE = HASHSIZE


class User(PersistentContainer):
    def __init__(self, name, email, password, parent=None):
        PersistentContainer.__init__(self, name, parent)
        self.email = email
        self.password_hash, self.password_salt = User.hash_password(password)
        self.__acl__ = [
            (Allow, Everyone, 'view'),
            (Allow, Everyone, 'login'),
            (Allow, Everyone, 'logout'),
            (Allow, name, 'edit'),
        ]

    def authenticate(self, password):
        hexhash = HASHCLASS(password + self.password_salt)
        return hexhash.hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password):
        password_salt = ''.join(
            random.choice(string.printable) for x in xrange(SALTSIZE)
        )
        hexhash = HASHCLASS(password + password_salt)
        return hexhash.hexdigest(), password_salt

def groupfinder(username, request):
    root = find_root(request.context)
    if username in root:
        user = root[username]
    else:
        #raise KeyError('Unknown user: %s' % username)
        return None
    return ()
    #return username
