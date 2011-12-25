 #!/usr/bin/python
 # -*- coding: utf-8 -*-

# set VS90COMNTOOLS=C:\Program Files\Microsoft Visual Studio 9.0\Common7\Tools

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///my.db', echo=True)
engine.execute("select 1").scalar()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('{0}', '{1}', '{2}')>".format(self.name, self.fullname, self.password)

# ed_user = User('ed', 'Ed Jones', 'edspassword')

Session = sessionmaker(bind=engine)
session = Session()

def InitData():
    Base.metadata.create_all(engine)
    session.add(ed_user)
    session.add_all([User('wendy', 'Wendy Williams', 'foobar'),
                     User('mary', 'Mary Contrary', 'xxg527'),
                     User('fred', 'Fred Flinstone', 'blah')])


def QueryAll():
    for u in session.query(User).order_by(User.id):
        print(u.name, u.fullname, u.password)

def QueryColumn():
    for t in session.query(User.name, User.fullname):
        print(dict(zip(t.keys(), t)))
        print(t)

def QueryTuple():
    for row in session.query(User, User.name).all():
        print(type(row))
        print(row.User, row.name)

def QueryByLabel():
    for row in session.query(User.name.label('name_label')).all():
        print(row.name_label)

from sqlalchemy.orm import aliased

def QueryAliased():
    ua = aliased(User, name='user_aliased')
    for row in session.query(ua, ua.name).all():
        print(row.user_aliased.name)

def Counting():
    print(session.query(User).filter(User.name.like('%ed')).count())

from sqlalchemy import func as sqlfunc
def CountIndicate():
    for u in session.query(sqlfunc.count(User.name), User.name).group_by(User.name).all():
        print(u)

def CountStar():
    print(session.query(sqlfunc.count(User.id)).scalar())

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

class Address(Base):
    '''The above class introduces the ForeignKey construct, which is a directive
    applied to Column that indicates that values in this column should be
    constrained to be values present in the named remote column. This is a core
    feature of relational databases, and is the “glue” that transforms an
    otherwise unconnected collection of tables to have rich overlapping
    relationships. The ForeignKey above expresses that values in the
    addresses.user_id column should be constrained to those values in the
    users.id column, i.e. its primary key.

    A second directive, known as relationship(), tells the ORM that the Address
    class itself should be linked to the User class, using the attribute
    Address.user. relationship() uses the foreign key relationships between the
    two tables to determine the nature of this linkage, determining that
    Address.user will be many-to-one. A subdirective of relationship() called
    backref() is placed inside of relationship(), providing details about the
    relationship as expressed in reverse, that of a collection of Address
    objects on User referenced by User.addresses. The reverse side of a
    many-to-one relationship is always one-to-many. A full catalog of available
    relationship() configurations is at Basic Relational Patterns.'''
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", backref=backref('addresses', order_by=id))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address
    
    










