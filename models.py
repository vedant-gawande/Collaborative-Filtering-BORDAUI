from sqlalchemy import Boolean, Column,Integer,String,ForeignKey,Text
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
    recommend = Column(String,default='') 
    recommendations = Column(String,default='')

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

class Videos(Base):
    __tablename__ = 'Videos'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    Category = Column(String) 
    Title = Column(String)
    Src = Column(String)
    Like = Column(Integer,default=0)
    Dislike = Column(Integer,default=0)
    Views = Column(Integer,default=0)

    
class Uinterest(Base):
    __tablename__ = 'Uinterest'
    id = Column(Integer, primary_key=True)
    Uid = Column(Integer, ForeignKey('Users.id'))
    UName = Column(String,ForeignKey('Users.username'))
    UEmail = Column(String,ForeignKey('Users.email'))
    Title = Column(String,ForeignKey('Videos.Title'))
    Src = Column(String,ForeignKey('Videos.Src'))
    Like = Column(Boolean, default=False)
    Dislike = Column(Boolean, default=False)
    Views = Column(Integer,default=0)
    Rating = Column(Integer,default=0)
    RatingRes = Column(Boolean,default=False)
    Description = Column(Text,default='')
    vid_id = Column(Integer,ForeignKey('Videos.id')) 

    def __repr__(self):
        return '<Uinterest %r>' % (self.id)
    
class Recommended_Vids(Base):
    __tablename__ = 'Recommended_Vids'
    id = Column(Integer, primary_key=True)
    Uid = Column(Integer)
    R_U_Videos = Column(String) 

class Req_list(Base):
    __tablename__ = 'Req_list'
    id = Column(Integer,primary_key=True,index=True)
    Uid = Column(Integer)
    req_list = Column(String) 