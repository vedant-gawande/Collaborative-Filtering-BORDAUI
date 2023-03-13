from fastapi import APIRouter, HTTPException,Request,Depends,status,responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database

router = APIRouter(
    prefix='/user_',
    tags=['User Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
def user_menu(request:Request):
    return templates.TemplateResponse('user_menu.html',{'request':request})
