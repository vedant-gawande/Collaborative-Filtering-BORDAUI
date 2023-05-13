from sklearn.cluster import KMeans
import numpy as np
from fastapi import Depends
from sqlalchemy.orm import Session
import models
from sklearn.preprocessing import MinMaxScaler

def cluster(db:Session):
    video_count = db.query(models.Videos).count()
    users = db.query(models.Users).all()
    matrix = []
    for user in users:
        list1 = [0]*video_count
        uinterest = db.query(models.Uinterest).filter(models.Uinterest.Uid == user.id).all()
        for uint in uinterest:
            list1[uint.vid_id-1] = int(uint.RatingRes)
        
        matrix.append(list1)

    # print(matrix)

    # Collect data
    # user_video_matrix = np.array([
    #     [1, 0, 1, 0, 1],  # User 1
    #     [0, 1, 1, 0, 0],  # User 2
    #     [1, 1, 0, 0, 0],  # User 3
    #     [0, 1, 1, 1, 0],  # User 4
    #     [0, 0, 0, 1, 1],  # User 5
    #     [1, 0, 0, 0, 1]   # User 6
    # ])
    user_video_matrix = np.array(matrix) 
    # print(user_video_matrix,matrix)

    # Normalize data
    # user_video_matrix_norm = user_video_matrix / np.linalg.norm(user_video_matrix, axis=1)[:, np.newaxis]
    # print(np.linalg.norm(user_video_matrix, axis=1)[:, np.newaxis])
    user_video_matrix_norm = MinMaxScaler().fit_transform(user_video_matrix)
    # print(user_video_matrix_norm)


    # Apply k-means clustering
    k = 3  # Number of clusters
    kmeans = KMeans(n_clusters=k, random_state=0).fit(user_video_matrix_norm)

    recom_vids = db.query(models.Recommended_Vids)
    recom_vids.delete(synchronize_session=False)
    db.commit()

    # Recommend videos
    
    user_cluster = kmeans.predict(user_video_matrix_norm)
    for user_id, cluster_id in enumerate(user_cluster):
        recommended_videos = np.where(kmeans.labels_ == cluster_id)[0]
        recommended_videos += 1
        recommended_videos = [str(i) for i in recommended_videos]
        recommended_videos.remove(str(user_id+1))
        # print(recommended_videos)
        recommended_videos = ','.join(recommended_videos)
        recom_vids = models.Recommended_Vids(Uid = user_id+1,R_U_Videos=recommended_videos)
        db.add(recom_vids)
        db.commit()
        db.refresh(recom_vids)
        # print(recommended_videos)
        # print(f"User {user_id+1} should watch videos {recommended_videos+1}")
