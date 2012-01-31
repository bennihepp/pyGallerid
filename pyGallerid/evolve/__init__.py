from collections import deque

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList

def walk_resources(root):
    dq = deque()
    dq.append(root)
    while len(dq) > 0:
        resource = dq.popleft()
        if isinstance(resource, Persistent):
            yield resource
        if isinstance(resource, PersistentDict):
            for name in resource:
                dq.append(resource[name])
        elif isinstance(resource, PersistentList):
            for child in resource:
                dq.append(child)
