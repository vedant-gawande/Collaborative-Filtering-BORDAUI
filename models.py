from sqlalchemy import Column,Integer,String
from database import Base


class Admin(Base):

    __tablename__ = 'Admin'

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    password = Column(String)

class Create_user(Base):

    __tablename__ = 'Users'

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    email = Column(String)
    password = Column(String)
    phone_number = Column(Integer)
    occupation = Column(String)