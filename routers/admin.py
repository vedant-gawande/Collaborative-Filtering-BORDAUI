from fastapi import APIRouter, Request,Depends,status,responses,Response,UploadFile,File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models,token_1,base64,io
import pandas as pd
import csv
import matplotlib.pyplot as plt
from repository.sort_requests import OpDB

router = APIRouter(
    prefix='/admin_',
    tags=['Admin Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
async def admin_menu(request:Request,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    return templates.TemplateResponse('admin_menu.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('view_users',response_class=HTMLResponse)
async def view_user(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    users_list = db.query(models.Users).all()
    return templates.TemplateResponse('viewUser.html',{'request':request,'users_list':users_list,'bool':True},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('search_users',response_class=HTMLResponse)
async def search_users(search_users,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    # form = await request.form()
    # string = form.get('search_users')
    string = search_users
    l1 = list(string)
    if bool(l1) and ' ' not in l1 :
        searched_users_list = db.query(models.Users).filter(models.Users.username == string)
        return templates.TemplateResponse('viewUser.html',{'request':request,'s_u_list':searched_users_list,'bool':False})
    else:
        return responses.RedirectResponse('/admin_view_users',status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})
    
@router.get('upload_dataset')
async def upload_dataset(request:Request,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    return templates.TemplateResponse('upload_dataset.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('viewDataset')
def viewDataset(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    OpDB.views(db)
    OpDB.likes_dislikes(db)
    videos = db.query(models.Videos).all()
    return templates.TemplateResponse('viewDataset.html',{'request':request,'videos':videos},headers={"Cache-Control": "no-store, must-revalidate"})


@router.post('operation_on_dataset')
async def operation_on_dataset(file:UploadFile = File(...),db:Session=Depends(get_db)):
    existing_data = db.query(getattr(models,'Videos'))
    result = existing_data.all()
    data = [obj.__dict__  for obj in result]
    existing_data = pd.DataFrame(data)
    if data:
        existing_data = existing_data.drop(['_sa_instance_state','id'], axis=1)
        existing_data = existing_data.reindex(columns=['Category','Title','Src'])
    # print(existing_data)
    contents = await file.read()
    dataset_str = contents.decode("Windows-1252")
    rows = csv.reader(dataset_str.splitlines())
    new_data = pd.DataFrame().from_records(rows)
    # print(new_data)
    required_cols = {'Category','Title','Src'}
    if required_cols.issubset(new_data.iloc[0]):
        new_data.columns = ['Category','Title','Src']
        new_data.drop(0,axis=0,inplace=True)
        all_data = pd.concat([existing_data,new_data]).drop_duplicates()
        videos = db.query(models.Videos)
        # videos.delete(synchronize_session=False)
        # db.commit()
        # videos = db.query(models.Videos)
        # print(videos.all())
        all_videos = videos.all()
        length = len(all_videos)
        Categories,Titles,links = ['']*length,['']*length,['']*length
        for index,video in enumerate(all_videos):
            Categories[index],Titles[index],links[index] = video.Category,video.Title,video.Src
        for _,row in all_data.iterrows():
            if not(row['Category'] in Categories and row['Title'] in Titles and row['Src'] in links):
                new_row = models.Videos(Category=row['Category'],Title=row['Title'],Src=row['Src'])
                db.merge(new_row)
        db.commit()
        return responses.RedirectResponse(url='/admin_viewDataset',status_code=302,headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        return responses.RedirectResponse(url='admin_menu',status_code=302,headers={"Cache-Control": "no-store, must-revalidate"})
    
@router.get('viewAllViews',response_class=HTMLResponse)
async def view_all_views_in_graph(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    dict_of_views = dict()
    views = db.query(models.Videos).all()
    for obj in views:
        if obj.Category in dict_of_views.keys():
            dict_of_views[obj.Category] += obj.Views
        else:
            dict_of_views[obj.Category] = obj.Views

    # print(dict_of_views)
    topics = list(dict_of_views.keys())
    values = list(dict_of_views.values())
    fig, ax = plt.subplots(figsize=(12.6, 6))
    ax.barh(topics, values)
    ax.set_xlabel('Number of Views')
    ax.set_title('Different Categories')
    plt.yticks(fontsize=10)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.clf()
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    return templates.TemplateResponse("viewAllViews.html", {"request": request, "chart_image": chart_image},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('viewAllLikesDislikes',response_class=HTMLResponse)
async def view_all_views_in_graph(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    dict_of_likes,dict_of_dislikes = dict(),dict()
    videos = db.query(models.Videos).all()
    for video in videos:
        if video.Category in dict_of_likes.keys():
            dict_of_likes[video.Category] += video.Like
        else:
            dict_of_likes[video.Category] = video.Like
    for video in videos:
        if video.Category in dict_of_dislikes.keys():
            dict_of_dislikes[video.Category] += video.Dislike
        else:
            dict_of_dislikes[video.Category] = video.Dislike
            
    topics = list(dict_of_likes.keys())

    # Extract the values for the likes and dislikes
    likes = list(dict_of_likes.values())
    dislikes = list(dict_of_dislikes.values())
    bar_width = 0.35
    r1 = range(len(likes))
    r2 = [x + bar_width for x in r1]
    fig = plt.figure(figsize=(12.5,6))
    plt.barh(r1, likes, color='green', height=bar_width, edgecolor='white', label='Likes')
    plt.barh(r2, dislikes, color='red', height=bar_width, edgecolor='white', label='Dislikes')
    plt.xlabel('Number of Likes and Dislikes')
    plt.title('Likes and Dislikes for different topics')
    plt.yticks([r + bar_width/2 for r in range(len(likes))], topics)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.clf()
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    return templates.TemplateResponse("viewAllLikesDislikes.html", {"request": request, "chart_image": chart_image},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('logout')
async def logout(request:Request,response:Response,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    response = templates.TemplateResponse('/admin_login.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})
    response.delete_cookie(key="access_token")
    return response