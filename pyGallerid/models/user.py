import random
import hashlib
import string

from pyramid.traversal import find_root

from . import PersistentContainer

HASHCLASS = hashlib.sha512
HASHSIZE = 2 * HASHCLASS().digest_size
SALTSIZE = HASHSIZE


class User(PersistentContainer):
    def __init__(self, name, email, password_hash, password_salt, parent=None):
        PersistentContainer.__init__(self, name, parent)
        self.email = email
        self.password_hash = password_hash
        self.password_salt = password_salt

    def authenticate(self, password):
        hexhash = HASHCLASS(password, self.password_salt)
        return hexhash.hexdigest() == self.password_hash

    @staticmethod
    def hash_password(password):
        password_salt = ''.join(
            random.choice(string.printable) for x in xrange(SALTSIZE)
        )
        hexhash = HASHCLASS(password + password_salt)
        return hexhash.hexdigest(), password_salt

def groupfinder(username, request):
    #user = find_interface(request.context, User)
    root = find_root(request.context)
    assert root is not None
    if username in root:
        user = root[username]
    else:
        raise KeyError('Unknown user: %s' % username)
    return username
