from fastapi import APIRouter,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/admin_'
)


templates = Jinja2Templates(directory='templates')

@router.get('login',response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse('admin_login.html',{"request":request})