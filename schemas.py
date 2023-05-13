from pydantic import BaseModel

class User(BaseModel):
    username : str
    email : str
    password : str
    phone_number : int
    occupation : str
    
class ShowUser(User):
    class Config():
        orm_mode = True