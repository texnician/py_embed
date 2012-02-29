#!/usr/bin/python
# -*- coding: utf-8 -*-

# set VS90COMNTOOLS=C:\Program Files\Microsoft Visual Studio 9.0\Common7\Tools

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func

#engine = create_engine('sqlite:///my.db', echo=True)
engine = create_engine('mysql+mysqldb://root:123@localhost/orm?charset=utf8', echo=True)
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
        return "<User('{0}', '{1}', '{2}'>".format(self.name, self.fullname, self.password)

class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    cardid = Column(Integer)
    level = Column(Integer)
    roleid = Column(Integer)

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    itemtype = Column(Integer)
    itemcount = Column(Integer)
    roleid = Column(Integer)
    
Base.metadata.create_all(engine)

# ed_user = User('ed', 'Ed Jones', 'edspassword')

Session = scoped_session(sessionmaker(bind=engine))
#Session = sessionmaker(bind=engine)
session = Session()
print(1, session)
# session.add(ed_user)
# session.add_all([User('tyg', 'Tang', '123'),
#                  User('lxj', 'Li', '456'),
#                  User('abc', 'ABC', '789')])
# session.commit()
#our_user = session.query(User).filter_by(name='ed').first()
u = session.query(User).filter(User.name=='tyg').one()
print(u)
print u in session
#Session.remove()
session.close()
# u.fullname = 'Tang'
session = Session()
print u in session
print(2, session)

#session.add(u)
#session.commit()
#print(our_user)

from sqlalchemy.sql import select, join, alias
cnt1 = alias(select([func.count('*')]).where(User.id <= 2))
cnt2 = alias(select([func.count('*')]).where(User.id >= 100))
cnt3 = alias(select([func.count('*')]).where(User.id == 7))
# r = session.execute(select(['*'], from_obj=[cnt1, cnt2, cnt3]))

def InitData():
    ss = Session()
    c1 = Card()
    c1.cardid = 1
    c1.level = 5
    c2 = Card()
    c2.cardid = 1
    c2.level = 7
    c3 = Card()
    c3.cardid = 2
    c3.level = 4
    c4 = Card()
    c4.cardid = 3
    c4.level = 1
    c5 = Card()
    c5.cardid = 4
    c5.level = 9
    cards = [c1, c2, c3, c4, c5]
    for c in cards:
        c.roleid = 2
    ss.add_all(cards)

    i1 = Item()
    i1.itemtype = 1
    i1.itemcount = 1
    i2 = Item()
    i2.itemtype = 1
    i2.itemcount = 1
    i3 = Item()
    i3.itemtype = 1
    i3.itemcount = 1
    i4 = Item()
    i4.itemtype = 1
    i4.itemcount = 1
    i5 = Item()
    i5.itemtype = 3
    i5.itemcount = 15
    i6 = Item()
    i6.itemtype = 5
    i6.itemcount = 2
    items = [i1,i2,i3,i4,i5,i6]
    for i in items:
        i.roleid = 2
    ss.add_all(items)
    ss.commit()

# InitData()


from sqlalchemy.sql import and_, or_, not_, bindparam, cast

class NodeCardNumGe(object):
    def __init__(self, cardid, num):
        self.cardid = cardid
        self.num = num
        self.query = select([func.count('*')],
                            and_(Card.roleid==bindparam('roleid', type_=Integer),
                                 Card.cardid==cardid))
        self.what = intern(':'.join([self.__class__.__name__, str(cardid), str(num)]))

class NodeCardLevelGe(object):
    def __init__(self, cardid, level):
        self.cardid = cardid
        self.level = level
        self.query = select([func.max(Card.level)],
                            and_(Card.roleid==bindparam('roleid', type_=Integer),
                                 Card.cardid==cardid))
        self.what = intern(':'.join([self.__class__.__name__, str(cardid), str(level)]))

class NodeItemNumGe(object):
    def __init__(self, itemtype, itemcount):
        self.itemtype = itemtype
        self.itemcount = itemcount
        self.query = select([cast(func.sum(Item.itemcount), Integer)],
                            and_(Item.roleid==bindparam('roleid', type_=Integer),
                                 Item.itemtype==itemtype))
        self.what = intern(':'.join([self.__class__.__name__, str(itemtype), str(itemcount)]))
        
node1 = NodeCardNumGe(1, 2)
node2 = NodeCardLevelGe(3, 4)
node3 = NodeItemNumGe(1, 3)

def ComposeNodeQuery(*nodes):
    return select(['*'], from_obj=[alias(n.query) for n in nodes])

from itertools import izip

def InitArgs(roleid, *nodes):
    q = ComposeNodeQuery(*nodes)
    r = session.execute(q, params={'roleid': roleid}).fetchone()
    print { n.what : i0 for n, i0 in izip(nodes, r) }
    
InitArgs(1, node1, node2, node3)
InitArgs(2, node1, node2, node3)

from sqlalchemy.orm import scoped_session
LocalSession = scoped_session(sessionmaker(bind=engine))

def InitData1():
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
