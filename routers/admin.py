from typing import Optional
from fastapi import APIRouter, HTTPException,Request,Depends,status,responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from hashing import Hash

router = APIRouter(
    prefix='/admin_',
    tags=['Admin Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
def admin_menu(request:Request):
    return templates.TemplateResponse('admin_menu.html',{'request':request})

@router.get('view_users',response_class=HTMLResponse)
def view_user(request:Request,db:Session=Depends(get_db)):
    users_list = db.query(models.Users).all()
    return templates.TemplateResponse('viewUser.html',{'request':request,'users_list':users_list,'bool':True})

@router.get('search_users',response_class=HTMLResponse)
def search_users(search_users,request:Request,db:Session=Depends(get_db)):
    # form = await request.form()
    # string = form.get('search_users')
    string = search_users
    l1 = list(string)
    if bool(l1) and ' ' not in l1 :
        searched_users_list = db.query(models.Users).filter(models.Users.username == string)
        return templates.TemplateResponse('viewUser.html',{'request':request,'s_u_list':searched_users_list,'bool':False})
    else:
        return responses.RedirectResponse('/admin_view_users',status_code=status.HTTP_302_FOUND)