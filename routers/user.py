from fastapi import APIRouter, Request,Depends,status,responses,Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from sqlalchemy import case,or_,text
from sqlalchemy.orm import Session
import database,models,token_1
from repository.sort_requests import OpDB
from algo import cluster

router = APIRouter(
    prefix='/user_',
    tags=['User Section'])

templates = Jinja2Templates(directory='templates')

get_db = database.get_db

@router.get('menu',response_class=HTMLResponse)
async def user_menu(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    OpDB.likes_dislikes(db)
    OpDB.views(db)
    cluster(db)
    user_token = token_1.get_token(request)
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    return templates.TemplateResponse('user_menu.html',{'request':request,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('profile',response_class=HTMLResponse)
async def user_profile(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    user_id = int(user_token.get("user_id"))
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == user_id).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    occ = db.query(models.Users).filter(models.Users.id == user_id).first().occupation
    total_friends = db.query(models.Users).filter(models.Users.id == user_id).first().friends
    if total_friends:
        total_friends = total_friends.split(',')
        if '' in total_friends:
            total_friends.remove('')
        total_friends = len(total_friends)
    total_friends = total_friends or 0 
    return templates.TemplateResponse('profile.html',{'request':request,'lname':user_token.get("sub"),'occupation':occ,'total_requests':total_requests,'total_friends':total_friends},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('terms',response_class=HTMLResponse)
async def user_terms(request:Request,db:Session=Depends(get_db)):
    return templates.TemplateResponse('terms_cond.html',{'request':request},headers={"Cache-Control": "no-store, must-revalidate"})


@router.get('uprofile',response_class=HTMLResponse)
async def user_uprofile(friend,request:Request,db:Session=Depends(get_db),jwt_validated:bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    user_id = int(user_token.get("user_id"))
    friend_id = db.query(models.Users).filter(models.Users.username == friend).first().id
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == friend_id).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    occ = db.query(models.Users).filter(models.Users.id == friend_id).first().occupation
    total_friends = db.query(models.Users).filter(models.Users.id == friend_id).first().friends
    if total_friends:
        total_friends = total_friends.split(',')
        if '' in total_friends:
            total_friends.remove('')
        total_friends = len(total_friends)
    total_friends = total_friends or 0 
    users_friends = db.query(models.Users).filter(models.Users.id == user_id).first().friends
    users_friends = users_friends.split(',')
    if '' in users_friends:
        users_friends.remove('')
    users_friends = users_friends or []
    requests = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == user_id).first()
    if requests:
        req_list = requests.sent_reqs
        if req_list:
            req_list = req_list.split(',')
            if '' in req_list:
                req_list.remove('')
    else:
        req_list = []
    OpDB.rec_requests(db,request)
    return templates.TemplateResponse('uprofile.html',{'request':request,'lname':user_token.get("sub"),'fr_name':friend,'occupation':occ,'total_requests':total_requests,'total_friends':total_friends,'users_friends':users_friends,'req_list':req_list,'friend_id':friend_id},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('uprofile_send_req',response_class=HTMLResponse)
async def send_requests(send_req,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    uid = send_req
    friend_name = db.query(models.Users).filter(models.Users.id == uid).first().username
    user_token = token_1.get_token(request)
    # print(type(uid))
    pre_req = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == int(user_token.get("user_id")))
    if not pre_req.first():
        new_req = models.Users_S_Req(uid=int(user_token.get("user_id")),sent_reqs=uid)
        db.add(new_req)
        db.commit()
        db.refresh(new_req)
        return responses.RedirectResponse(f"/user_uprofile?friend={friend_name}",headers={"Cache-Control": "no-store, must-revalidate"})
    pre_req1 = pre_req.first()
    list_req = pre_req1.sent_reqs.split(',')
    if '' in list_req:
        list_req.remove('')
    list_req.append(uid)
    list_req = sorted(set(list_req))
    # print(list_req)
    pre_req.update({'sid':pre_req1.sid,'uid':pre_req1.uid,'sent_reqs':",".join(list_req)})
    db.commit()
    return responses.RedirectResponse(f"/user_uprofile?friend={friend_name}",headers={"Cache-Control": "no-store, must-revalidate"})



@router.get('credits',response_class=HTMLResponse)
async def credits(request:Request,db:Session=Depends(get_db)):
    user_token = token_1.get_token(request)
    return templates.TemplateResponse('credits.html',{'request':request,'lname':user_token.get("sub")},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('view_users',response_class=HTMLResponse)
async def view_user(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    users_list = db.query(models.Users,models.Users_S_Req).outerjoin(models.Users_S_Req,models.Users_S_Req.uid == models.Users.id).order_by(text("RANDOM()")).all()
    user_token = token_1.get_token(request)
    user_id = int(user_token.get("user_id"))
    friends = db.query(models.Users).filter(models.Users.id == user_id).first().friends
    friends = friends or []
    req_list = []
    for index,user in enumerate(users_list):
        # print(index,user[0].friends)
        if user[0].id == user_id:
            if user[1]:
                req_list = user[1].sent_reqs.split(',')
                if '' in req_list:
                    req_list.remove('')
                # Getset.set_req_list(req_list)
                OpDB.mng_req_list(user_id,db,req_list)
                req_list = [int(i) for i in req_list] 
            users_list.pop(index)
            break
    new_users_list = [l[0] for l in users_list]
    OpDB.rec_requests(db,request)
    # print(req_list,friends)
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    return templates.TemplateResponse('searchUser.html',{'request':request,'users_list':new_users_list,'req_list':req_list,'friends':friends,'bool':True,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('search_users',response_class=HTMLResponse)
async def search_users(search_value,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    user_id = int(user_token.get("user_id"))
    friends = db.query(models.Users).filter(models.Users.id == user_id).first().friends
    friends = friends or []
    string = search_value
    l1 = string.split(' ')
    OpDB.rec_requests(db,request)
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    if bool(l1) and '' not in l1 :
        req_list = db.query(models.Req_list).filter(models.Req_list.Uid == user_id).first()
        if req_list:
            req_list = req_list.req_list
        if req_list:
            req_list = req_list.split(" ")
            if ' ' in req_list:
                req_list.remove(' ')
            req_list = [int(i) for i in req_list]
        else:
            req_list = []
        if user_token.get("sub") != string:
            searched_users_list = db.query(models.Users).filter(models.Users.username == string)
            # print(searched_users_list.first(),Getset.get_req_list())    #for code testing and i.e. to check output and code flow
            return templates.TemplateResponse('searchUser.html',{'request':request,'s_u_list':searched_users_list,'req_list':req_list,'bool':False,'friends':friends,'lname':user_token.get("sub")},headers={"Cache-Control": "no-store, must-revalidate"})
        else:
            searched_users_list = db.query(models.Users).filter(models.Users.username == ' ')
            return templates.TemplateResponse('searchUser.html',{'request':request,'s_u_list':searched_users_list,'req_list':req_list,'bool':False,'friends':friends,'lname':user_token.get("sub")},headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        # print(string,l1)              #for code testing and i.e. to check output and code flow 
        return responses.RedirectResponse('/user_view_users',status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})
    

@router.get('send_req',response_class=HTMLResponse)
async def send_requests(send_req,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    uid = send_req
    user_token = token_1.get_token(request)
    # print(type(uid))
    pre_req = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == int(user_token.get("user_id")))
    if not pre_req.first():
        new_req = models.Users_S_Req(uid=int(user_token.get("user_id")),sent_reqs=uid)
        db.add(new_req)
        db.commit()
        db.refresh(new_req)
        return responses.RedirectResponse('/user_view_users',headers={"Cache-Control": "no-store, must-revalidate"})
    pre_req1 = pre_req.first()
    list_req = pre_req1.sent_reqs.split(',')
    if '' in list_req:
        list_req.remove('')
    list_req.append(uid)
    list_req = sorted(set(list_req))
    # print(list_req)
    pre_req.update({'sid':pre_req1.sid,'uid':pre_req1.uid,'sent_reqs':",".join(list_req)})
    db.commit()
    return responses.RedirectResponse('/user_view_users',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('request',response_class=HTMLResponse)
async def requests(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    users_list = db.query(models.Users,models.Users_R_Req).outerjoin(models.Users_R_Req,models.Users_R_Req.uid == models.Users.id).all()
    req_list = []
    user_token = token_1.get_token(request)
    for index,user in enumerate(users_list):
        # print(index,user)
        if user[0].id == int(user_token.get("user_id")):
            if user[1]:
                req_list = user[1].rec_reqs.split(',')
                if '' in req_list:
                    req_list.remove('')
                OpDB.mng_req_list(int(user_token.get("user_id")),db,req_list)
                req_list = [int(i) for i in req_list] 
            users_list.pop(index)
            break
    new_users_list = [l[0] for l in users_list]
    # print(req_list)
    return templates.TemplateResponse('userReq.html',{'request':request,'lname':user_token.get("sub"),'users':new_users_list,'req_list':req_list,'bool':True},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('search_req',response_class=HTMLResponse)
async def search_requests(search_value,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    users_list = db.query(models.Users,models.Users_R_Req).outerjoin(models.Users_R_Req,models.Users_R_Req.uid == models.Users.id).all()
    user_token = token_1.get_token(request)
    string = search_value
    l1 = string.split(' ')
    new_users_list = db.query(models.Users).filter(models.Users.username == string)
    req_list = db.query(models.Req_list).filter(models.Req_list.Uid == int(user_token.get("user_id"))).first()
    if req_list:
        req_list = req_list.req_list
    # print(req_list)
    if req_list:
        req_list = req_list.split(" ")
        if ' ' in req_list:
            req_list.remove(' ')
        req_list = [int(i) for i in req_list]
    else:
        req_list = []
    if bool(l1) and '' not in l1:
        if string!=user_token.get("sub"):
            for user in users_list:
                if user[0].username == string:
                    new_users_list = user
                    break
            # print(new_users_list[0],req_list)
            new_users_list = new_users_list[0] or []
            return templates.TemplateResponse('userReq.html',{'request':request,'users':new_users_list[0],'req_list':req_list,'lname':user_token.get("sub"),'bool':False},headers={"Cache-Control": "no-store, must-revalidate"})
        else:
            return templates.TemplateResponse('userReq.html',{'request':request,'users':new_users_list,'req_list':req_list,'bool':False,'lname':user_token.get("sub")},headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        return responses.RedirectResponse('/user_request',status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('operate_req',response_class=HTMLResponse)
async def operate_req(req_status,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    # print(req_status)
    OpDB.friend_mgmt(req_status,db,request)
    return responses.RedirectResponse('/user_request',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('friend_list',response_class=HTMLResponse)
async def friend_list(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id")))
    users = db.query(models.Users).all()
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    fr_list = []
    if user.first().friends:
        fr_list = user.first().friends.split(',')
    fr_fr_list = []
    if '' in fr_list:
        fr_list.remove('')
    for friend in fr_list:
        fr_fr = db.query(models.Users).filter(models.Users.id==friend).first()
        if fr_fr.friends:
            list_of_fr_fr = fr_fr.friends.split(',')
            if user_token.get("user_id") in list_of_fr_fr:
                list_of_fr_fr.remove(user_token.get("user_id"))
            list_of_friends = []
            for fr in list_of_fr_fr:
                for user1 in users:
                    if user1.id == int(fr) and user_token.get("sub") != user1.username:
                        list_of_friends.append(user1.username)
            list_of_friends = ','.join(list_of_friends)
            fr_fr_list.append(list_of_friends)
    return templates.TemplateResponse('friendList.html',{'request':request,'users':users,'fr_list':fr_list,'fr_fr_list':fr_fr_list,'bool':True,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('search_friend_list',response_class=HTMLResponse)
async def search_friend_list(search_value,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    string = search_value
    user_token = token_1.get_token(request)
    l1 = string.split(' ')
    users = db.query(models.Users).all()
    user_friend_list = db.query(models.Users).filter(models.Users.username == user_token.get("sub")).first().friends
    # user_friend_list = user_friend_list.friends
    if user_friend_list:
        user_friend_list = user_friend_list.split(',')
    fr_list=''
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    if bool(l1) and '' not in l1 :
        searched_users_list = db.query(models.Users).filter(models.Users.username == string).first()
        if user_token.get("sub") != string and searched_users_list and (str(searched_users_list.id) in user_friend_list):
            friends_list,fr_list = searched_users_list.friends,[]
            if friends_list:
                for friend in friends_list:
                    for user in users:
                        if friend == str(user.id) and user_token.get("sub") != user.username:
                            fr_list.append(user.username)
                fr_list = ', '.join(fr_list)    
            return templates.TemplateResponse('friendList.html',{'request':request,'user':searched_users_list,'fr_list':fr_list,'bool':False,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})
        else:
            searched_users_list = db.query(models.Users).filter(models.Users.username == ' ')
            return templates.TemplateResponse('friendList.html',{'request':request,'user':searched_users_list,'fr_list':fr_list,'bool':False,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        # print(string,l1)              #for code testing and i.e. to check output and code flow 
        return responses.RedirectResponse('/user_friend_list',status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})
    
@router.get('unfollow',response_class=HTMLResponse)
async def see_videos(unfollow_id,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    user_id = user_token.get("user_id")
    # print(unfollow_id,type(user_id))
    user = db.query(models.Users).filter(models.Users.id == user_id)
    friend = db.query(models.Users).filter(models.Users.id == int(unfollow_id))
    user_friends = user.first().friends
    user_friends = user_friends.split(',')
    if '' in user_friends:
        user_friends.remove('')
    user_friends.remove(unfollow_id)        #removed friend from user's friends
    friend_friends = friend.first().friends
    friend_friends = friend_friends.split(',')
    if '' in friend_friends:
        friend_friends.remove('')
    # print(friend_friends,[user_id])
    friend_friends.remove(str(user_id))          #removed user from friend's friends
    user.update({'friends':",".join(user_friends)})
    friend.update({'friends':",".join(friend_friends)})
    db.commit()
    return responses.RedirectResponse('/user_friend_list',status_code=status.HTTP_302_FOUND,headers={"Cache-Control": "no-store, must-revalidate"})
    
@router.get('view_videos',response_class=HTMLResponse)
async def see_videos(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    Recommended_user_videos = db.query(models.Recommended_Vids).filter(models.Recommended_Vids.Uid == int(user_token.get("user_id"))).first().R_U_Videos
    if Recommended_user_videos:
        list_of_users = Recommended_user_videos.split(',')
        if '' in list_of_users:
            list_of_users.remove('')
        list_of_users,video_ids = [int(i) for i in list_of_users],[]
        video_query = db.query(models.Uinterest).filter(models.Uinterest.Uid.in_(list_of_users),or_(models.Uinterest.Like==1,models.Uinterest.RatingRes==1))
        for video in video_query:
            video_ids.append(video.vid_id)
        id_ordering = case(*[(models.Videos.id == value,index) for index,value in enumerate(video_ids)])
        # print(id_ordering,video_ids)
        # if video_ids:
        if str(id_ordering) != 'CASE END':
            videos = db.query(models.Videos).order_by(id_ordering.desc(),text("RANDOM()")).offset(10).all()
        else:
            videos = db.query(models.Videos).order_by(text("RANDOM()")).offset(10).all()
        #     videos = db.query(models.Videos).all()
    else:
        videos = db.query(models.Videos).order_by(text("RANDOM()")).offset(10).all()
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id"))).first()
    recommended_videos = ''
    if user and user.recommend:
        recommended_videos = user.recommend
    OpDB.likes_dislikes(db)
    OpDB.views(db)
    return templates.TemplateResponse("view_Videos.html", {"request":request,'lname':user_token.get("sub"),"videos":videos,'recommend':recommended_videos,'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"}) 

@router.get('videos/li_di/{video_id}')
async def like_dislike(lik_di,video_id:int,request:Request,db:Session=Depends(get_db),boolean:Optional[bool]=True,jwt_validated: bool = Depends(token_1.verify_token)):
    user_token = token_1.get_token(request)
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id"))).first()
    video = db.query(models.Videos).filter(models.Videos.id == video_id).first()

    value = int(lik_di)
    like = True if value else False 
    dislike = not(like)
    uinterest = db.query(models.Uinterest).filter(models.Uinterest.vid_id == video_id,models.Uinterest.Uid == int(user_token.get("user_id")))
    if not uinterest.first():
        add_uinterest = models.Uinterest(Uid = int(user_token.get("user_id")),UName = user.username,UEmail = user.email,
                                         Title = video.Title,Src = video.Src,Like = like,Dislike = dislike,vid_id = video.id)
        db.add(add_uinterest)
        db.commit()
        db.refresh(add_uinterest)
    else:
        uinterest.update({'Like':like,'Dislike':dislike})
        db.commit()
    OpDB.likes_dislikes(db)
    OpDB.views(db)
    if boolean:
        return responses.RedirectResponse('/user_view_videos',headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        return responses.RedirectResponse('/user_recommended_videos',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('videos_recommend/{video_id}')
async def recommend_videos(video_id:int,request:Request,db:Session=Depends(get_db),boolean:Optional[bool]=True,jwt_validated: bool = Depends(token_1.verify_token)):
    user_token = token_1.get_token(request)
    friends = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id"))).first().friends
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id")))
    if friends:
        friends = friends.split(',')
        if '' in friends:
            friends.remove('')
        friends = [int(i) for i in friends]
    for id in friends:
        friend = db.query(models.Users).filter(models.Users.id == id)
        recommendations = friend.first().recommendations
        recommend = user.first().recommend
        if recommendations==None or recommendations=='':
            recommendations = str(video_id)
        else:
            recommendations = recommendations.split(',')
            recommendations.append(str(video_id))
            recommendations = sorted(set(recommendations))
            recommendations = ','.join(recommendations)
        friend.update({'recommendations':recommendations})
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
    OpDB.likes_dislikes(db)
    OpDB.views(db)
    if boolean:
        return responses.RedirectResponse('/user_view_videos',headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        return responses.RedirectResponse('/user_recommended_videos',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('video_rating/{video_id}')
async def video_rating(video_id:int,request:Request,boolean:Optional[bool]=True,jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    return templates.TemplateResponse('rating.html',{'request':request,'video_id':video_id,'boolean':boolean,'lname':user_token.get("sub")},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('video_rating/cal_rating/{video_id}')
async def cal_rating(star:int,boolean:bool,descript,video_id:int,request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    user_token = token_1.get_token(request)
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id"))).first()
    video = db.query(models.Videos).filter(models.Videos.id == video_id).first()
    value=0
    if star>2:
        value=1
    uinterest = db.query(models.Uinterest).filter(models.Uinterest.id == video_id,models.Uinterest.Uid == int(user_token.get("user_id")))
    if not uinterest.first():
        add_uinterest = models.Uinterest(Uid = int(user_token.get("user_id")),UName = user.username,UEmail = user.email,
                                         Title = video.Title,Src = video.Src,Rating = star, RatingRes = value,Description = descript,vid_id = video.id)
        db.add(add_uinterest)
        db.commit()
        db.refresh(add_uinterest)
    else:
        uinterest.update({'Rating':star,'RatingRes':value,'Description':descript})
        db.commit()
    if boolean:
        return responses.RedirectResponse('/user_view_videos',headers={"Cache-Control": "no-store, must-revalidate"})
    else:
        return responses.RedirectResponse('/user_recommended_videos',headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('recommended_videos',response_class=HTMLResponse)
async def recommended_videos_to_user(request:Request,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    total_requests = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(user_token.get("user_id"))).scalar()
    if total_requests:
        total_requests = total_requests.rec_reqs.split(',')
        if '' in total_requests:
            total_requests.remove('')
        total_requests = len(total_requests)
    total_requests = total_requests or 0
    user = db.query(models.Users).filter(models.Users.id == int(user_token.get("user_id"))).first()
    Recommended_user_videos = db.query(models.Recommended_Vids).filter(models.Recommended_Vids.Uid == int(user_token.get("user_id"))).first().R_U_Videos
    if Recommended_user_videos:
        list_of_users = Recommended_user_videos.split(',')
        if '' in list_of_users:
            list_of_users.remove('')
        list_of_users,video_ids = [int(i) for i in list_of_users],[]
        video_query = db.query(models.Uinterest).filter(models.Uinterest.Uid.in_(list_of_users),models.Uinterest.RatingRes==1)
        for video in video_query:
            video_ids.append(video.vid_id)
        id_ordering = case(*[(models.Videos.id == value,index) for index,value in enumerate(video_ids)])
        if str(id_ordering) != 'CASE END':
            videos = db.query(models.Videos).order_by(id_ordering.desc(),text("RANDOM()"))
        else:
            videos = db.query(models.Videos).order_by(text("RANDOM()"))
    else:
        videos = db.query(models.Videos).order_by(text("RANDOM()"))
    recommended_videos = user.recommendations
    # videos = db.query(models.Videos).all()
    if recommended_videos:
        recommended_videos = recommended_videos.split(',')
        recommended_videos = sorted(map(int,recommended_videos))
    else:
        recommended_videos = []
    recommended_videos_to = ''
    if user.recommend:
        recommended_videos_to = user.recommend
    OpDB.likes_dislikes(db)
    OpDB.views(db)
    return templates.TemplateResponse('recommended_videos.html',{'request':request,'videos':videos,'recommend_from':recommended_videos,'recommend_to':recommended_videos_to,'lname':user_token.get("sub"),'total_requests':total_requests},headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('open_video/{vid_id}')
async def open_video(url1,request:Request,vid_id:int,db:Session=Depends(get_db),jwt_validated: bool = Depends(token_1.verify_token)):
    if jwt_validated != True:
        return jwt_validated
    user_token = token_1.get_token(request)
    uinterest = db.query(models.Uinterest).filter(models.Uinterest.vid_id == vid_id,models.Uinterest.Uid == int(user_token.get("user_id")))
    uint = uinterest.first()
    if uint:
        views = uint.Views
        # print(views)
        uinterest.update({'Views':views+1})
        db.commit()
    else:
        video = db.query(models.Videos).filter(models.Videos.id == vid_id).first()
        user = db.query(models.Users).filter(models.Users.username == user_token.get("sub")).first()
        add_uint = models.Uinterest(Uid = user.id,UName = user.username,UEmail = user.email,Title = video.Title,Src = video.Src,vid_id = vid_id,Views = 1)
        db.add(add_uint)
        db.commit()
        db.refresh(add_uint)
    return responses.RedirectResponse(url1,headers={"Cache-Control": "no-store, must-revalidate"})

@router.get('logout')
async def logout(request:Request,response:Response,db:Session=Depends(get_db)):
    # if jwt_validated != True:
    #     return jwt_validated
    user_token = token_1.get_token(request)
    req_list = db.query(models.Req_list).filter(models.Req_list.Uid == int(user_token.get("user_id")))
    if req_list.first():
        req_list.delete(synchronize_session=False)
        db.commit()
    response = responses.RedirectResponse('/user_login', headers={"Cache-Control": "no-store, must-revalidate"})
    response.delete_cookie(key="access_token")
    return response