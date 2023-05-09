from fastapi import APIRouter,Request,Depends,responses,status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from hashing import Hash
from algo import cluster


get_db = database.get_db


router = APIRouter(tags=['start_menu'])


templates = Jinja2Templates(directory='templates')

@router.get('/',response_class=HTMLResponse)
async def default_router(db:Session=Depends(get_db)):
    cluster(db)
    return responses.RedirectResponse('/user_login',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('/admin_login',response_class=HTMLResponse)
def login(request:Request,db:Session=Depends(get_db)):
    cluster(db)
    return templates.TemplateResponse('admin_login.html',{"request":request},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('/user_login',response_class=HTMLResponse)
def login(request:Request,db:Session=Depends(get_db)):
    cluster(db)
    return templates.TemplateResponse('user_login.html',{"request":request},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('/register_page',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse('register.html',{"request":request},headers={"Cache-Control": "no-store, must-revalidate"})

@router.post('/register_user',response_class=HTMLResponse)
async def register_user(request:Request,db:Session = Depends(get_db)):
    form = await request.form()
    usernames = db.query(models.Users.username).all()
    emails = db.query(models.Users.email).all()
    usernames,emails = [i[0] for i in usernames],[i[0] for i in emails] 
    if form.get('reg_name') in usernames:
        return templates.TemplateResponse('register.html',{'request':request,'msg':'Username already exists'})
    if form.get('reg_email') in emails:
        return templates.TemplateResponse('register.html',{'request':request,'msg':'Email already exists'})
    new_user = models.Users(username = form.get('reg_name'),email = form.get('reg_email'),
                                  password = Hash.bcrypt(form.get('reg_password')),
                                  phone_number = form.get('reg_phone_number') , occupation = form.get('reg_occupation'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return responses.RedirectResponse('/user_login',status_code=303,headers={"Cache-Control": "no-store, must-revalidate"})