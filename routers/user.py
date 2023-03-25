from typing import Optional
from fastapi import APIRouter, Request,Depends,status,responses
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import database,models
from routers.getset import Getset
from repository.sort_requests import OpDB

router = APIRouter(
    prefix='/user_',
    tags=['User Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
def user_menu(request:Request):
    return templates.TemplateResponse('user_menu.html',{'request':request})

@router.get('view_users',response_class=HTMLResponse)
def view_user(request:Request,db:Session=Depends(get_db)):
    users_list = db.query(models.Users,models.Users_S_Req).join(models.Users_S_Req,models.Users_S_Req.uid == models.Users.id,full=True).all()
    friends = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first().friends
    req_list = []
    for index,user in enumerate(users_list):
        print(index,user[0].friends)
        if user[0].id == Getset.get_uid():
            if user[1]:
                req_list = user[1].sent_reqs.split(',')
                if '' in req_list:
                    req_list.remove('')
                req_list = [int(i) for i in req_list] 
                Getset.set_req_list(req_list)
            users_list.pop(index)
            break
    new_users_list = [l[0] for l in users_list]
    OpDB.rec_requests(db)
    return templates.TemplateResponse('searchUser.html',{'request':request,'users_list':new_users_list,'req_list':req_list,'friends':friends,'bool':True})

@router.get('search_users',response_class=HTMLResponse)
def search_users(search_value,request:Request,db:Session=Depends(get_db)):
    string = search_value
    l1 = string.split(' ')
    OpDB.rec_requests(db)
    if bool(l1) and '' not in l1 :
        if Getset.lname != string:
            searched_users_list = db.query(models.Users).filter(models.Users.username == string)
            print(searched_users_list.first(),Getset.get_req_list())    #for code testing and i.e. to check output and code flow
            return templates.TemplateResponse('searchUser.html',{'request':request,'s_u_list':searched_users_list,'req_list':Getset.get_req_list(),'bool':False})
        else:
            searched_users_list = db.query(models.Users).filter(models.Users.username == ' ')
            return templates.TemplateResponse('searchUser.html',{'request':request,'s_u_list':searched_users_list,'req_list':Getset.get_req_list(),'bool':False})
    else:
        # print(string,l1)              #for code testing and i.e. to check output and code flow 
        return responses.RedirectResponse('/user_view_users',status_code=status.HTTP_302_FOUND)
    

@router.get('send_req',response_class=HTMLResponse)
def send_requests(send_req,request:Request,db:Session=Depends(get_db)):
    uid = send_req
    # print(type(uid))
    pre_req = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == Getset.get_uid())
    if not pre_req.first():
        new_req = models.Users_S_Req(uid=Getset.get_uid(),sent_reqs=uid)
        db.add(new_req)
        db.commit()
        db.refresh(new_req)
        return responses.RedirectResponse('/user_view_users')
    pre_req1 = pre_req.first()
    list_req = pre_req1.sent_reqs.split(',')
    if '' in list_req:
        list_req.remove('')
    list_req.append(uid)
    list_req = sorted(set(list_req))
    # print(list_req)
    pre_req.update({'sid':pre_req1.sid,'uid':pre_req1.uid,'sent_reqs':",".join(list_req)})
    db.commit()
    return responses.RedirectResponse('/user_view_users')

@router.get('request',response_class=HTMLResponse)
def requests(request:Request,db:Session=Depends(get_db)):
    users_list = db.query(models.Users,models.Users_R_Req).join(models.Users_R_Req,models.Users_R_Req.uid == models.Users.id,full=True).all()
    req_list = []
    for index,user in enumerate(users_list):
        # print(index,user)
        if user[0].id == Getset.get_uid():
            if user[1]:
                req_list = user[1].rec_reqs.split(',')
                if '' in req_list:
                    req_list.remove('')
                req_list = [int(i) for i in req_list] 
                Getset.set_req_list(req_list)
            users_list.pop(index)
            break
    new_users_list = [l[0] for l in users_list]
    # print(req_list)
    return templates.TemplateResponse('userReq.html',{'request':request,'users':new_users_list,'req_list':req_list,'bool':True})

@router.get('search_req',response_class=HTMLResponse)
def search_requests(search_value,request:Request,db:Session=Depends(get_db)):
    users_list = db.query(models.Users,models.Users_R_Req).join(models.Users_R_Req,models.Users_R_Req.uid == models.Users.id,full=True).all()
    string = search_value
    l1 = string.split(' ')
    new_users_list = db.query(models.Users).filter(models.Users.username == string)
    req_list = Getset.get_req_list()
    if bool(l1) and '' not in l1:
        if string!=Getset.get_lname():
            for user in users_list:
                if user[0].username == string:
                    new_users_list = user
                    break
            print(new_users_list[0])
            return templates.TemplateResponse('userReq.html',{'request':request,'users':new_users_list[0],'req_list':req_list,'bool':False})
        else:
            return templates.TemplateResponse('userReq.html',{'request':request,'users':new_users_list,'req_list':req_list,'bool':False})
    else:
        return responses.RedirectResponse('/user_request',status_code=status.HTTP_302_FOUND)

@router.get('operate_req',response_class=HTMLResponse)
def operate_req(req_status,db:Session=Depends(get_db)):
    # print(req_status)
    OpDB.friend_mgmt(req_status,db)
    return responses.RedirectResponse('/user_request')

@router.get('friend_list',response_class=HTMLResponse)
def friend_list(request:Request,db:Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid())
    users = db.query(models.Users).all()
    fr_list = []
    if user.first():
        fr_list = user.first().friends.split(',')
    fr_fr_list = []
    if '' in fr_list:
        fr_list.remove('')
    for friend in fr_list:
        fr_fr = db.query(models.Users).filter(models.Users.id==friend).first()
        if fr_fr.friends:
            list_of_fr_fr = fr_fr.friends.split(',')
            if str(Getset.get_uid()) in list_of_fr_fr:
                list_of_fr_fr.remove(str(Getset.get_uid()))
            list_of_friends = []
            for fr in list_of_fr_fr:
                for user1 in users:
                    if user1.id == int(fr):
                        list_of_friends.append(user1.username)
            fr_fr_list.append(list_of_friends:=', '.join(list_of_friends))
    return templates.TemplateResponse('friendList.html',{'request':request,'users':users,'fr_list':fr_list,'fr_fr_list':fr_fr_list,'bool':True})

@router.get('search_friend_list',response_class=HTMLResponse)
def search_friend_list(search_value,request:Request,db:Session=Depends(get_db)):
    string = search_value
    l1 = string.split(' ')
    users = db.query(models.Users).all()
    user_friend_list = db.query(models.Users).filter(models.Users.username == Getset.get_lname()).first().friends
    # user_friend_list = user_friend_list.friends
    if user_friend_list:
        user_friend_list = user_friend_list.split(',')
    fr_list=''
    if bool(l1) and '' not in l1 :
        searched_users_list = db.query(models.Users).filter(models.Users.username == string).first()
        if Getset.get_lname() != string and searched_users_list and (str(searched_users_list.id) in user_friend_list):
            friends_list,fr_list = searched_users_list.friends,[]
            if friends_list:
                for friend in friends_list:
                    for user in users:
                        if friend == str(user.id) and Getset.get_lname() != user.username:
                            fr_list.append(user.username)
                fr_list = ', '.join(fr_list)    
            return templates.TemplateResponse('friendList.html',{'request':request,'user':searched_users_list,'fr_list':fr_list,'bool':False})
        else:
            searched_users_list = db.query(models.Users).filter(models.Users.username == ' ')
            return templates.TemplateResponse('friendList.html',{'request':request,'user':searched_users_list,'fr_list':fr_list,'bool':False})
    else:
        # print(string,l1)              #for code testing and i.e. to check output and code flow 
        return responses.RedirectResponse('/user_friend_list',status_code=status.HTTP_302_FOUND)
    
@router.get('view_videos',response_class=HTMLResponse)
def see_videos(request:Request,db:Session=Depends(get_db)):
    videos = db.query(models.Videos).order_by(models.Videos.id.asc())
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first()
    recommended_videos = ''
    if user.recommend:
        recommended_videos = user.recommend
    return templates.TemplateResponse("view_Videos.html", {"request":request,"videos":videos,'recommend':recommended_videos}) 

@router.get('videos/li_di/{video_id}')
def like_dislike(lik_di,video_id:int,db:Session=Depends(get_db),boolean:Optional[bool]=True):
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first()
    video = db.query(models.Videos).filter(models.Videos.id == video_id).first()
    value = int(lik_di)
    like = True if value else False 
    dislike = not(like)
    uinterest = db.query(models.Uinterest).filter(models.Uinterest.vid_id == video_id,models.Uinterest.Uid == Getset.get_uid())
    if not uinterest.first():
        add_uinterest = models.Uinterest(Uid = Getset.get_uid(),UName = user.username,UEmail = user.email,
                                         Title = video.Title,Src = video.Src,Like = like,Dislike = dislike,vid_id = video.id)
        db.add(add_uinterest)
        db.commit()
        db.refresh(add_uinterest)
    else:
        uinterest.update({'Like':like,'Dislike':dislike})
        db.commit()
    if boolean:
        return responses.RedirectResponse('/user_view_videos')
    else:
        return responses.RedirectResponse('/user_recommended_videos')

@router.get('videos_recommend/{video_id}')
def recommend_videos(video_id:int,db:Session=Depends(get_db),boolean:Optional[bool]=True):
    friends = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first().friends
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid())
    if friends:
        friends = friends.split(',')
        if '' in friends:
            friends.remove('')
        friends = [int(i) for i in friends]
    for id in friends:
        friend = db.query(models.Users).filter(models.Users.id == id)
        recommended = friend.first().recommended
        recommend = user.first().recommend
        if recommended==None or recommended=='':
            recommended = str(video_id)
        else:
            recommended = recommended.split(',')
            recommended.append(str(video_id))
            recommended = sorted(set(recommended))
            recommended = ','.join(recommended)
        friend.update({'recommended':recommended})
        db.commit()
        if recommend==None or recommend=='':
            recommend = str(video_id)
        else:
            recommend = recommend.split(',')
            recommend.append(str(video_id))
            recommend = sorted(set(recommend))
            recommend = ','.join(recommend)
        user.update({'recommend':recommend})
        db.commit()
    if boolean:
        return responses.RedirectResponse('/user_view_videos')
    else:
        return responses.RedirectResponse('/user_recommended_videos')

@router.get('video_rating/{video_id}')
def video_rating(video_id:int,request:Request,boolean:Optional[bool]=True):
    return templates.TemplateResponse('rating.html',{'request':request,'video_id':video_id,'boolean':boolean})

@router.get('video_rating/cal_rating/{video_id}')
async def cal_rating(star:int,boolean:bool,descript,video_id:int,request:Request,db:Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first()
    video = db.query(models.Videos).filter(models.Videos.id == video_id).first()
    value=0
    if star>2:
        value=1
    uinterest = db.query(models.Uinterest).filter(models.Uinterest.id == video_id,models.Uinterest.Uid == Getset.get_uid())
    if not uinterest.first():
        add_uinterest = models.Uinterest(Uid = Getset.get_uid(),UName = user.username,UEmail = user.email,
                                         Title = video.Title,Src = video.Src,Rating = star, RatingRes = value,Description = descript,vid_id = video.id)
        db.add(add_uinterest)
        db.commit()
        db.refresh(add_uinterest)
    else:
        uinterest.update({'Rating':star,'RatingRes':value,'Description':descript})
        db.commit()
    if boolean:
        return responses.RedirectResponse('/user_view_videos')
    else:
        return responses.RedirectResponse('/user_recommended_videos')

@router.get('recommended_videos',response_class=HTMLResponse)
def recommended_videos_to_user(request:Request,db:Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == Getset.get_uid()).first()
    recommended_videos = user.recommended
    videos = db.query(models.Videos).all()
    if recommended_videos:
        recommended_videos = recommended_videos.split(',')
        recommended_videos = sorted(map(int,recommended_videos))
    else:
        recommended_videos = []
    recommended_videos_to = ''
    if user.recommend:
        recommended_videos_to = user.recommend
    return templates.TemplateResponse('recommended_videos.html',{'request':request,'videos':videos,'recommend_from':recommended_videos,'recommend_to':recommended_videos_to})