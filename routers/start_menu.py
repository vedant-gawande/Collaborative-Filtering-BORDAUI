from fastapi import APIRouter,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


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