class Getset:
    lname,uid='user1',1
    req_list = []

    @classmethod
    def get_lname(cls):
        return cls.lname
    
    @classmethod
    def set_lname(cls,lname:str):
        cls.lname = lname
    
    @classmethod
    def get_uid(cls):
        return cls.uid
    
    @classmethod
    def set_uid(cls,uid:int):
        cls.uid = uid

    @classmethod
    def get_req_list(cls):
        return cls.req_list
    
    @classmethod
    def set_req_list(cls,req_list:list):
        cls.req_list = req_list