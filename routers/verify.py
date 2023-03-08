from fastapi import APIRouter, HTTPException,Request,Depends,status,responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from hashing import Hash

router = APIRouter(
    prefix='/verify_',
    tags=['Verify Admin or User'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.post('admin',response_class= HTMLResponse )
async def verify_admin(request:Request,db:Session = Depends(get_db)):
    form = await request.form()
    user = db.query(models.Admin).filter(models.Admin.username == form.get('username')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Invalid Credentials')
    
    if not Hash.verify(form.get('password'),user.password):
        return templates.TemplateResponse('admin_login.html',{'request':request})
    
    return responses.RedirectResponse('/admin_menu')

@router.post('user',response_class= HTMLResponse )
async def verify_admin(request:Request,db:Session = Depends(get_db)):
    form = await request.form()
    print(form.get('username'))
    user = db.query(models.Create_user).filter(models.Create_user.username == form.get('username')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Invalid Credentials')
    
    if not Hash.verify(form.get('password'),user.password):
        return templates.TemplateResponse('user_login.html',{'request':request})
    
    return responses.RedirectResponse('user_menu.html',status_code=status.HTTP_302_FOUND)
    