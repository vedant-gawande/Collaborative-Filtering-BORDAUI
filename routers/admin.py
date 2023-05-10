from fastapi import APIRouter, Request,Depends,status,responses,Response,UploadFile,File
from fastapi.responses import HTMLResponse,FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func,desc
import database,models,token_1
import pandas as pd
import csv,base64,tempfile
from repository.sort_requests import OpDB
from plotly.subplots import make_subplots
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from io import StringIO,BytesIO
from xhtml2pdf import pisa

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
    avg_ratings = db.query(func.sum(models.Uinterest.Rating)).filter(models.Uinterest.Rating > 0).scalar()/db.query(func.count(models.Uinterest.Rating)).filter(models.Uinterest.Rating > 0).scalar()
    # print(avg_ratings)
    videos = db.query(func.count(models.Videos.id)).scalar()
    users = db.query(func.count(models.Users.id)).scalar()
    return templates.TemplateResponse('admin_menu.html',{'request':request,'views':views,'likes':likes,'dislikes':dislikes,'avg_ratings':round(avg_ratings,1),'videos':videos,'users':users},headers={"Cache-Control": "no-store, must-revalidate"})

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

@router.get('remove_user')
async def upload_dataset(send_req,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_id = int(send_req)
    user_sent_reqs = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == user_id)
    if user_sent_reqs.first() and user_sent_reqs.first().sent_reqs:
        req_list = user_sent_reqs.first().sent_reqs.split(',')
        if '' in req_list:
            req_list.remove('')
        for fr_id in req_list:
            friend = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(fr_id))
            if friend.first() and friend.first().rec_reqs:
                fr_req_list = friend.first().rec_reqs
                fr_req_list = fr_req_list.split(',')
                if '' in fr_req_list:
                    fr_req_list.remove('')
                fr_req_list.remove(send_req)
                friend.update({"rec_reqs":",".join(fr_req_list)})
    user_sent_reqs.delete(synchronize_session=False)
    db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == user_id).delete(synchronize_session=False)
    db.query(models.Recommended_Vids).filter(models.Recommended_Vids.Uid == user_id).delete(synchronize_session=False)
    db.query(models.Uinterest).filter(models.Uinterest.Uid == user_id).delete(synchronize_session=False)
    user = db.query(models.Users).filter(models.Users.id == user_id)
    if user.first().friends:
        friends = user.first().friends.split(',')
        if '' in friends:
            friends.remove('')
        for friend_id in friends:
            friend = db.query(models.Users).filter(models.Users.id == int(friend_id))
            friend_list = friend.first().friends
            if friend_list:
                friend_list = friend_list.split(',')
                if '' in friend_list:
                    friend_list.remove('')
                if send_req in friend_list:
                    friend_list.remove(send_req)
            friend.update({"friends":",".join(friend_list)})
    user.delete(synchronize_session=False)
    db.commit()
    recom_vids = db.query(models.Recommended_Vids).all()
    for i, recom_vid in enumerate(recom_vids,start=1):
        recom_vid.id = i
    db.commit()
    return responses.RedirectResponse("/admin_view_users",status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('viewDataset')
def viewDataset(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    OpDB.views(db)
    OpDB.likes_dislikes(db)
    videos = db.query(models.Videos).all()
    df = pd.DataFrame.from_records([video.__dict__ for video in videos])
    df = df.drop(columns=['_sa_instance_state'])
    df = df.reindex(columns=['id','Category','Title','Views','Like','Dislike'])
    df = df.rename(columns={'id':'Sr.No.','Category':'CATEGORY','Title':'TITLE','Views':'VIEWS','Like':'LIKES','Dislike':'DISLIKES'})
    csv_str = StringIO()
    df.to_csv(csv_str,index=False)
    csv_str.seek(0)
    csv_data = csv_str.read()
    b64_data = base64.b64encode(csv_data.encode("utf-8")).decode("utf-8")
    data_uri = "data:text/csv;base64," + b64_data
    # print(csv_data)
    return templates.TemplateResponse('viewDataset.html',{'request':request,'videos':videos,'csvfile':data_uri},headers={"Cache-Control": "no-store, must-revalidate"})


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
    dataset_str = contents.decode("utf-8")
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

@router.get('gen_report')
def generate_report(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    total_views = db.query(func.sum(models.Videos.Views)).scalar()
    total_likes = db.query(func.sum(models.Videos.Like)).scalar()
    total_dislikes = db.query(func.sum(models.Videos.Dislike)).scalar()
    total_vids = db.query(func.count(models.Videos.id)).scalar()
    total_users = db.query(func.count(models.Users.id)).scalar()
    df = pd.DataFrame([["All Views","Likes","Dislikes","Total Vid","Total Users"],[total_views,total_likes,total_dislikes,total_vids,total_users],[" "," "," "," "," "]])
    
    ################################## Views Report ############################################
    
    row4 = [" "," ","Views Report"," "," "]
    row5 = [" "," "," "," "," "]
    row6 = ["All Views", " -> ",total_views," "," "]
    row7 = [" "," "," "," "," "]
    row8,row9 = ["Categories","Views"," % "," "," "],[" "," "," "," "," "]
    df.loc[4],df.loc[5],df.loc[6],df.loc[7],df.loc[8],df.loc[9] = row4,row5,row6,row7,row8,row9
    categories = db.query(models.Videos.Category).distinct().all()
    categories = [category[0] for category in categories]
    multi_use_list = [[],[]]
    for category in categories:
        one_cat_view = db.query(func.sum(models.Videos.Views)).filter(models.Videos.Category == category).scalar()
        multi_use_list[0].append(one_cat_view)
        multi_use_list[1].append(round((one_cat_view/total_views)*100,2))
    new_dict = {0:categories,1:multi_use_list[0],2:multi_use_list[1]}
    new_df = pd.DataFrame(new_dict)
    df = df.append(new_df,ignore_index=True)

    ################################## Likes Report ############################################
    
    rows = [[" "," "," "," "," "],[" "," ","Likes Report"," "," "],[" "," "," "," "," "],["All Likes", " -> ",total_likes," "," "],[" "," "," "," "," "],["Categories","Likes"," % "," "," "],[" "," "," "," "," "]]
    row_len = len(df)
    for row in rows:
        df.loc[row_len] = row
        row_len += 1
    multi_use_list = [[],[]]
    for category in categories:
        one_cat_like = db.query(func.sum(models.Videos.Like)).filter(models.Videos.Category == category).scalar()
        multi_use_list[0].append(one_cat_like)
        multi_use_list[1].append(round((one_cat_like/total_likes)*100,2))
    new_dict = {0:categories,1:multi_use_list[0],2:multi_use_list[1]}
    new_df = pd.DataFrame(new_dict)
    df = df.append(new_df,ignore_index=True) 

    ################################## Dislikes Report ############################################
    
    rows = [[" "," "," "," "," "],[" "," ","Dislikes Report"," "," "],[" "," "," "," "," "],["All Dislikes", " -> ",total_dislikes," "," "],[" "," "," "," "," "],["Categories","Dislikes"," % "," "," "],[" "," "," "," "," "]]
    row_len = len(df)
    for row in rows:
        df.loc[row_len] = row
        row_len += 1
    multi_use_list = [[],[]]
    for category in categories:
        one_cat_dislike = db.query(func.sum(models.Videos.Dislike)).filter(models.Videos.Category == category).scalar()
        multi_use_list[0].append(one_cat_dislike)
        multi_use_list[1].append(round((one_cat_dislike/total_dislikes)*100,2))
    new_dict = {0:categories,1:multi_use_list[0],2:multi_use_list[1]}
    new_df = pd.DataFrame(new_dict)
    df = df.append(new_df,ignore_index=True)

    ################################## Video Report ############################################
    
    rows = [[" "," "," "," "," "],[" "," ","Video Report"," "," "],[" "," "," "," "," "],["All Videos", " -> ",total_vids," "," "],[" "," "," "," "," "],[" ","Top 10","Trending","Videos"," "],[" "," "," "," "," "]]
    row_len = len(df)
    for row in rows:
        df.loc[row_len] = row
        row_len += 1
    multi_use_list = [[],[]]
    videos = db.query(models.Videos).order_by(desc(models.Videos.Views)).limit(10).all()
    videos = [video.Title for video in videos]
    new_dict = {0:videos}
    new_df = pd.DataFrame(new_dict)
    df = df.append(new_df,ignore_index=True)

    ################################## Rating Report ############################################
    
    avg_rating = db.query(func.sum(models.Uinterest.Rating)).filter(models.Uinterest.Rating > 0).scalar()/db.query(func.count(models.Uinterest.Rating)).filter(models.Uinterest.Rating > 0).scalar()
    rows = [[" "," "," "," "," "],[" "," ","Rating Report"," "," "],[" "," "," "," "," "],["Avg. Rating", " -> ",avg_rating," "," "],[" "," "," "," "," "],["Categories","Avg.Rating"," "," "," "],[" "," "," "," "," "]]
    row_len = len(df)
    for row in rows:
        df.loc[row_len] = row
        row_len += 1
    multi_use_list = [[],[]]
    cat_avg_ratings = db.query(models.Videos.Category,func.coalesce(func.avg(models.Uinterest.Rating),0)).outerjoin(models.Uinterest,models.Videos.id == models.Uinterest.vid_id).group_by(models.Videos.Category).all()
    for cat in cat_avg_ratings:
        multi_use_list[0].append(cat[0])
        multi_use_list[1].append(cat[1])
    new_dict = {0:multi_use_list[0],1:multi_use_list[1]}
    new_df = pd.DataFrame(new_dict)
    df = df.append(new_df,ignore_index=True)

    ################################## User Report ############################################
    
    rows = [[" "," "," "," "," "],["User Report"," "," "," "," "],[" "," "," "," "," "],["Total Users", " -> ",total_users," "," "],[" "," "," "," "," "]]
    row_len = len(df)
    for row in rows:
        df.loc[row_len] = row
        row_len += 1
    df.fillna(" ",inplace=True)
    # print(df)
    ############################# Converting data to csv #######################################
    csv_str = StringIO()
    df.to_csv(csv_str,index=False)
    csv_str.seek(0)
    csv_data = csv_str.read()
    b64_data = base64.b64encode(csv_data.encode("utf-8")).decode("utf-8")
    csv_file = "data:text/csv;base64," + b64_data

    ############################# Converting data to pdf #######################################
    
    table_html = df.to_html(index=False,header=False,border=0)

    styles = """
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
    }
    td, th {
        text-align: left;
        font-size: 14px;
        padding-top: 0.5rem;
    }
    td {
        border: none;
    }
    </style>
    """

    # Generate PDF from HTML table
    pdf = BytesIO()
    pisa.CreatePDF(StringIO(styles + table_html), pdf)
    pdf.seek(0)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf.getvalue())
        temp_file.seek(0)
        file_path = temp_file.name

    return templates.TemplateResponse("report.html", {"request": request,"csv_file":csv_file,"pdf":file_path},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get("download_pdf")
async def download_report_pdf(file_path: str):
    return FileResponse(file_path, media_type="application/pdf", filename="report.pdf")

@router.get('logout')
async def logout(request:Request,response:Response,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    response = templates.TemplateResponse('/admin_login.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})
    response.delete_cookie(key="access_token")
    return response