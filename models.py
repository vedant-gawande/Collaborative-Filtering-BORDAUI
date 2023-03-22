from sqlalchemy import Column,Integer,String,ForeignKey
from database import Base


class Admin(Base):

    __tablename__ = 'Admin'

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    password = Column(String)

class Users(Base):

    __tablename__ = 'Users'

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    email = Column(String)
    password = Column(String)
    phone_number = Column(Integer)
    occupation = Column(String)
    friends = Column(String) 

class Users_S_Req(Base):

    __tablename__ = 'User_S_Requests'

    sid = Column(Integer,primary_key=True,index=True)
    uid = Column(Integer,ForeignKey('Users.id'))
    sent_reqs = Column(String) 

class Users_R_Req(Base):

    __tablename__ = 'User_R_Requests'

    rid = Column(Integer,primary_key=True,index=True)
    uid = Column(Integer,ForeignKey('Users.id'))
    rec_reqs = Column(String)