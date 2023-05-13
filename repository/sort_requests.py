from fastapi import Request
from sqlalchemy.orm import Session
import models,token_1
class OpDB:
    def rec_requests(db:Session,request:Request):
        user_token = token_1.get_token(request)
        uid = int(user_token.get("user_id"))
        user = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == uid).first()
        if user:
            req_list = user.sent_reqs.split(',')
            if '' in req_list:
                req_list.remove('')
            req_list = [int(i) for i in req_list]
            for i in req_list:
                req_rec = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == i)
                if not req_rec.first():
                    new_req = models.Users_R_Req(uid=i,rec_reqs=uid)
                    db.add(new_req)
                    db.commit()
                    db.refresh(new_req)
                else:
                    req_rec1 = req_rec.first()
                    list_req = req_rec1.rec_reqs.split(',')
                    if '' in list_req:
                        list_req.remove('')
                    list_req.append(str(uid))
                    list_req = sorted(set(list_req))
                    # print(list_req)
                    req_rec.update({'rid':req_rec1.rid,'uid':req_rec1.uid,'rec_reqs':",".join(list_req)})
                    db.commit()
            # print(req_list)

    def friend_mgmt(req_status,db:Session,request:Request):
        user_token = token_1.get_token(request)
        user_id = int(user_token.get("user_id"))
        operate_req_list = req_status.split(',')
        uid,status = operate_req_list[0],operate_req_list[1]
        update_user = db.query(models.Users).filter(models.Users.id == user_id)
        update_user1 = update_user.first()
        friends = update_user1.friends
        if status == "ACCEPT":
            if not friends:
                friends = ''
            fr_l = friends.split(',')
            if '' in fr_l:
                fr_l.remove('')
            fr_l.append(uid)    
            fr_l = sorted(set(fr_l))
            fr_l = ','.join(fr_l)
            update_user.update({'friends':fr_l})
            db.commit()
            #adding friend for other user
            update_user = db.query(models.Users).filter(models.Users.id == uid)
            update_user1 = update_user.first()
            friends = update_user1.friends
            if not friends:
                friends = ''
            fr_l = friends.split(',')
            if '' in fr_l:
                fr_l.remove('')
            fr_l.append(str(user_id))
            fr_l = sorted(set(fr_l))
            fr_l = ','.join(fr_l)
            update_user.update({'friends':fr_l})
            db.commit()
        rem_friend = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == user_id)
        rem_friend1 = rem_friend.first()
        fr_id = rem_friend1.rec_reqs.split(',')
        fr_id.remove(uid)
        fr_id = ','.join(fr_id)
        rem_friend.update({'rec_reqs':fr_id})
        db.commit()
        rem_friend = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == int(uid))
        rem_friend1 = rem_friend.first()
        fr_id = rem_friend1.sent_reqs.split(',')
        fr_id.remove(str(user_id))
        fr_id = ','.join(fr_id)
        rem_friend.update({'sent_reqs':fr_id})
        db.commit()
        rem_friend = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == user_id)
        if rem_friend.first():
            rem_friend1 = rem_friend.first()
            fr_id = rem_friend1.sent_reqs.split(',')
            if uid in fr_id:
                fr_id.remove(uid)
                fr_id = ','.join(fr_id)
                rem_friend.update({'sent_reqs':fr_id})
                db.commit()
        rem_friend = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == int(uid))
        if rem_friend.first():
            rem_friend1 = rem_friend.first()
            fr_id = rem_friend1.rec_reqs.split(',')
            if str(user_id) in fr_id:
                fr_id.remove(str(user_id))
                fr_id = ','.join(fr_id)
                rem_friend.update({'rec_reqs':fr_id})
                db.commit()

    def likes_dislikes(db:Session):
        join = db.query(models.Uinterest.vid_id).join(models.Videos,models.Uinterest.vid_id==models.Videos.id).distinct(models.Videos.id).order_by(models.Videos.id)
        # print(join[0][0])
        for i in join:
            likes,dislikes = 0,0
            uinters = db.query(models.Uinterest).filter(models.Uinterest.vid_id==i[0])
            video = db.query(models.Videos).filter(models.Videos.id==i[0])
            for uint in uinters:
                if uint.Like:
                    likes+=1 
                else:
                    dislikes+=1
            video.update({'Like':likes,'Dislike':dislikes})
            db.commit()
            # print(uinters)

    def views(db:Session):
        join = db.query(models.Uinterest.vid_id).join(models.Videos,models.Uinterest.vid_id==models.Videos.id).distinct(models.Videos.id).order_by(models.Videos.id)
        for i in join:
            v_views = 0
            uinters = db.query(models.Uinterest).filter(models.Uinterest.vid_id==i[0])
            video = db.query(models.Videos).filter(models.Videos.id==i[0])
            for uint in uinters:
                v_views += uint.Views
                # print(uint.Views)
            video.update({'Views':v_views})
            db.commit()

    def mng_req_list(Uid:int,db:Session,req_list):
        req_list_query = db.query(models.Req_list).filter(models.Req_list.Uid == Uid)
        if req_list_query.first():
            req_list = ','.join(req_list)
            req_list_query.update({'req_list':req_list})
            db.commit()
        else:
            ReqList = models.Req_list(Uid=Uid,req_list = ",".join(req_list))
            db.add(ReqList)
            db.commit()
            db.refresh(ReqList)
        pass