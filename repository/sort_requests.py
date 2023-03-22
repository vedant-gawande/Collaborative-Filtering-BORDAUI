from routers.getset import Getset
from sqlalchemy.orm import Session
import models
class OpDB:
    def rec_requests(db:Session):
        uid = Getset.get_uid()
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

    def friend_mgmt(req_status,db:Session):
        operate_req_list = req_status.split(',')
        uid,status = operate_req_list[0],operate_req_list[1]
        update_user = db.query(models.Users).filter(models.Users.id == Getset.get_uid())
        update_user1 = update_user.first()
        friends = update_user1.friends
        if status == "ACCEPT":
            if not friends:
                friends = ''
            fr_l = friends.split(',')
            if '' in fr_l:
                fr_l.remove('')
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
            fr_l.append(str(Getset.get_uid()))
            fr_l = sorted(set(fr_l))
            fr_l = ','.join(fr_l)
            update_user.update({'friends':fr_l})
            db.commit()
        rem_friend = db.query(models.Users_R_Req).filter(models.Users_R_Req.uid == Getset.get_uid())
        rem_friend1 = rem_friend.first()
        fr_id = rem_friend1.rec_reqs.split(',')
        fr_id.remove(uid)
        fr_id = ','.join(fr_id)
        rem_friend.update({'rec_reqs':fr_id})
        db.commit()
        rem_friend = db.query(models.Users_S_Req).filter(models.Users_S_Req.uid == int(uid))
        rem_friend1 = rem_friend.first()
        fr_id = rem_friend1.sent_reqs.split(',')
        fr_id.remove(str(Getset.get_uid()))
        fr_id = ','.join(fr_id)
        rem_friend.update({'sent_reqs':fr_id})
        db.commit()