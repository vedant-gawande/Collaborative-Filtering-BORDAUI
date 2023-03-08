from fastapi import APIRouter,Request,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from hashing import Hash


get_db = database.get_db


router = APIRouter(tags=['start_menu'])


templates = Jinja2Templates(directory='templates')

@router.get('/admin_login',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse('admin_login.html',{"request":request})

@router.get('/user_login',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse('user_login.html',{"request":request})

@router.get('/register_page',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse('register.html',{"request":request})

@router.post('/register_user',response_class=HTMLResponse)
async def register_user(request:Request,db:Session = Depends(get_db)):
    form = await request.form()
    new_user = models.Create_user(username = form.get('reg_name'),email = form.get('reg_email'),
                                  password = Hash.bcrypt(form.get('reg_password')),
                                  phone_number = form.get('reg_phone_number') , occupation = form.get('reg_occupation'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse('admin_login.html',{"request":request})