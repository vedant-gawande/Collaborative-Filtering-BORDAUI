from fastapi import APIRouter, Request,Depends,status,responses,Response,UploadFile,File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import database,models,token_1
import pandas as pd
import csv
from repository.sort_requests import OpDB
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

router = APIRouter(
    prefix='/admin_',
    tags=['Admin Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
async def admin_menu(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    views = db.query(func.sum(models.Videos.Views)).scalar()
    likes = db.query(func.sum(models.Videos.Like)).scalar()
    dislikes = db.query(func.sum(models.Videos.Dislike)).scalar()
    videos = db.query(func.count(models.Videos.id)).scalar()
    users = db.query(func.count(models.Users.id)).scalar()
    return templates.TemplateResponse('admin_menu.html',{'request':request,'views':views,'likes':likes,'dislikes':dislikes,'videos':videos,'users':users},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('profile',response_class=HTMLResponse)
async def admin_profile(request:Request,db:Session=Depends(get_db)):
    user_token = token_1.get_token(request)
    return templates.TemplateResponse('aprofile.html',{'request':request,'lname':user_token.get("sub")})

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
    df = pd.DataFrame.from_records([video.__dict__ for video in videos])
    df = df.drop(columns=['_sa_instance_state'])
    df = df.reindex(columns=['id','CATEGORY','TITLE','VIEWS','LIKES','DISLIKES'])
    print(df.columns)
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
        print(new_data.iloc[0])
        new_data.columns = new_data.iloc[0]
        new_data = new_data.loc[:,['Category','Title','Src']]
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

    # Create a list of categories and views
    categories = list(dict_of_views.keys())
    views = list(dict_of_views.values())

    # Create a subplots object with one bar chart
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(
        go.Bar(x=categories, y=np.zeros(len(categories))),
        row=1, col=1
    )

    # Define the frames for the animation
    frames = [go.Frame(data=[go.Bar(x=categories, y=views[:i+1])]) for i in range(len(views))]

    # Define the animation settings
    animation_settings = dict(
        frame=dict(duration=1000, redraw=True),
        fromcurrent=True
    )

    # Add the frames to the animation
    fig.frames = frames

    # Define the layout
    fig.update_layout(
        title='Different Categories',
        xaxis=dict(title='Category'),
        yaxis=dict(title='Number of Views')
    )

    # Define the animation buttons
    fig.update_layout(
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            buttons=[dict(
                label='Play',
                method='animate',
                args=[None, animation_settings]
            )]
        )]
    )

    # Convert the figure to HTML
    chart_html = fig.to_html(full_html=False)

    return templates.TemplateResponse("viewAllViews.html", {"request": request, "chart_html": chart_html},headers={"Cache-Control": "no-store, must-revalidate"})

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

    fig = px.bar(x=topics, y=likes, color_discrete_sequence=['green'], labels={'x': 'Category', 'y': 'Number of Likes'}, 
                 title='Likes and Dislikes for different topics')
    fig.add_bar(x=topics, y=dislikes, name='Dislikes', marker_color='red')

    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Number of Likes/Dislikes",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="black"
        ),
        bargap=0.3,
        bargroupgap=0.1,
        template='plotly_white'
    )

    chart_div = fig.to_html(full_html=False)

    return templates.TemplateResponse("viewAllLikesDislikes.html", {"request": request, "chart_div": chart_div},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('logout')
async def logout(request:Request,response:Response,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    response = templates.TemplateResponse('/admin_login.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})
    response.delete_cookie(key="access_token")
    return response