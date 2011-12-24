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
        return "<User('{0}', '{1}', '{2}'>".format(self.name, self.fullname, self.password)

Base.metadata.create_all(engine)

ed_user = User('ed', 'Ed Jones', 'edspassword')

Session = sessionmaker(bind=engine)
session = Session()
session.add(ed_user)
session.add_all([User('wendy', 'Wendy Williams', 'foobar'),
                 User('mary', 'Mary Contrary', 'xxg527'),
                 User('fred', 'Fred Flinstone', 'blah')])
#our_user = session.query(User).filter_by(name='ed').first()
#print(our_user)
