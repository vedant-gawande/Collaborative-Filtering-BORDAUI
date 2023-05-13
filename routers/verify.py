from fastapi import APIRouter, HTTPException,Request,Depends,status,responses,Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models,token_1
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
    
    data = {'sub':user.username,'user_id':user.id}
    access_token = token_1.create_access_token(data=data)
    response = responses.RedirectResponse('/admin_menu',status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token",value=f"Bearer {access_token}",httponly=True)
    
    return response

@router.post('user',response_class= HTMLResponse )
async def verify_user(request:Request,response:Response,db:Session = Depends(get_db)):
    form = await request.form()
    user = db.query(models.Users).filter(models.Users.username == form.get('username')).first()
    if not user:
        return templates.TemplateResponse('user_login.html',{'request':request})
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Invalid Credentials')
    
    if not Hash.verify(form.get('password'),user.password):
        return templates.TemplateResponse('user_login.html',{'request':request})
    
    data = {'sub':user.username,'user_id':user.id}
    access_token = token_1.create_access_token(data=data)
    response = responses.RedirectResponse('/user_menu',status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token",value=f"Bearer {access_token}",httponly=True)
    return response

    