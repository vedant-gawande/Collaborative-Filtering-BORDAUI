from fastapi import APIRouter, HTTPException,Request,Depends,status,responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from hashing import Hash

router = APIRouter(
    prefix='/admin_',
    tags=['Verify Admin or User'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.post('menu',response_class=HTMLResponse)
def admin_menu(request:Request):
    return templates.TemplateResponse('admin_menu.html',{'request':request})

@router.get('view_users',response_class=HTMLResponse)
def view_user(request:Request):
    pass