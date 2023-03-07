from sqlalchemy import Column,Integer,String
from database import Base

class create_user(Base):

    __tablename__ = 'Users'

    id = Column(Integer,primary_key=True,index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    phone_number = Column(Integer)
    occupation = Column(String)