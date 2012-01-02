from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
)

from sqlalchemy.orm.collections import (
    attribute_mapped_collection,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
