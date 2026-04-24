from datetime import datetime, timedelta
import json
import os
import time
import traceback
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlmodel.ext.asyncio.session import AsyncSession as Session
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sqlmodel import select
from sklearn.manifold import TSNE

from core.settings import DataSettings, DATA_SET_PATH
from core.http import ErrorCode, get_common_response
from core.security import current_active_user
from model import get_session, ClusterExperiment
from schemas.experiment import *


experiment_router = APIRouter()


@experiment_router.post("/create")
async def create_experiment(
    min_clusters: int = Form(...),
    max_clusters: int = Form(...),
    session: Session = Depends(get_session),
    # current_user: User = Depends(current_active_user)
):
    try:
        # 1. 读取并预处理数据
        df = pd.read_csv(
            DATA_SET_PATH,
            dtype={
                "user_id": "int32", "item_id": "int32",
                "behavior_type": "int8",
                "item_category": "int8",
            }
        )
        
        print(df.info(memory_usage="deep"))
        
        # 2. 数据预处理
        # 处理时间字段
        df["date"] = df["time"].map(lambda x: x.split()[0])
        df["hour"] = df["time"].map(lambda x: x.split()[1])
        df["date"] = pd.to_datetime(df["date"])
        df["hour"] = df["hour"].astype("int64")
        
        # 构造特征
        visit_cnt = df.groupby(by=["user_id"]).size()
        trans_rate = (
            df.groupby(by=["user_id"])["behavior_type"].agg(lambda x: x[x==4].size)
            / visit_cnt
        )
        life_cycle = df.groupby(by=["user_id"])["date"].agg(lambda x: (max(x) - min(x)).days)
        
        # 合并特征
        features = pd.DataFrame({
            "visit_cnt": visit_cnt,
            "trans_rate": trans_rate,
            "life_cycle": life_cycle,
        })
        
        # 标准化
        scaler = StandardScaler()
        X = scaler.fit_transform(features)
        
        # 3. 对每个聚类数进行聚类并计算轮廓系数
        results = []
        for n_clusters in range(min_clusters, max_clusters + 1):
            start_time = time.time()
            
            # 聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            kmeans.fit(X)

            # 获取每个簇对应的样本数量
            cluster_counts = pd.Series(kmeans.labels_).value_counts()
            cluster_counts_path = os.path.join(DataSettings.DATA_PATH, f"cluster_counts_{n_clusters}.json")
            with open(cluster_counts_path, 'w') as f:
                f.write(cluster_counts.to_json())
            
            # TSNE降维
            tsne = TSNE(n_components=2, random_state=42)
            X_tsne = tsne.fit_transform(X)
            
            # 构造降维结果数据
            tsne_result = pd.DataFrame({
                'x': X_tsne[:, 0],
                'y': X_tsne[:, 1],
                'cluster_id': kmeans.labels_
            })
            
            # 保存TSNE结果
            tsne_path = os.path.join(DataSettings.DATA_PATH, f"tsne_result_{n_clusters}.json")
            with open(tsne_path, 'w') as f:
                f.write(tsne_result.to_json(orient='records'))
            
            # 计算轮廓系数
            sil_score = silhouette_score(X, kmeans.labels_)
            
            # 计算运行时间
            run_time = time.time() - start_time
            
            # 查找是否存在相同cluster_num的记录
            query = select(ClusterExperiment).where(ClusterExperiment.cluster_num == n_clusters)
            result = await session.execute(query)
            existing_experiment = result.first()
            
            if existing_experiment:
                # 如果存在，则更新记录
                existing_experiment[0].silhouette_score = float(sil_score)
                existing_experiment[0].run_time = float(run_time)
                session.add(existing_experiment[0])
            else:
                # 如果不存在，则新增记录
                experiment = ClusterExperiment(
                    cluster_num=n_clusters,
                    silhouette_score=float(sil_score),
                    run_time=float(run_time)
                )
                session.add(experiment)
            
            # 添加到结果数组
            results.append({
                "cluster_num": n_clusters,
                "silhouette_score": sil_score,
                "run_time": run_time
            })
        await session.commit()
        return get_common_response(ErrorCode.success, data=results)
    except Exception as e:
        traceback.print_exc()
        return get_common_response(error_code=ErrorCode.internal_error)


@experiment_router.post("/info")
async def get_experiment_info(
    body: ClusterExperimentQuerySchema,
    session: Session = Depends(get_session),
):
    try:
        # 1. 获取实验记录
        query = select(ClusterExperiment).where(ClusterExperiment.cluster_num == body.cluster_num)
        result = await session.execute(query)
        experiment = result.first()
        
        if not experiment:
            return get_common_response(error_code=ErrorCode.not_found, msg="未找到对应的实验记录")
        
        # 2. 读取簇样本分布
        cluster_counts_path = os.path.join(DataSettings.DATA_PATH, f"cluster_counts_{body.cluster_num}.json")
        if not os.path.exists(cluster_counts_path):
            return get_common_response(error_code=ErrorCode.not_found, msg="未找到簇样本分布数据")
        
        with open(cluster_counts_path, 'r') as f:
            cluster_counts = json.load(f)
        
        # 3. 读取TSNE降维结果
        tsne_path = os.path.join(DataSettings.DATA_PATH, f"tsne_result_{body.cluster_num}.json")
        if not os.path.exists(tsne_path):
            return get_common_response(error_code=ErrorCode.not_found, msg="未找到TSNE降维结果")
        
        with open(tsne_path, 'r') as f:
            tsne_result = json.load(f)
        
        # 4. 构造返回数据
        response_data = {
            "experiment_info": {
                "cluster_num": body.cluster_num,
                "silhouette_score": experiment[0].silhouette_score,
                "run_time": experiment[0].run_time
            },
            "cluster_counts": cluster_counts,
            "tsne_result": tsne_result
        }
        
        return get_common_response(ErrorCode.success, data=response_data)
    except Exception as e:
        traceback.print_exc()
        return get_common_response(error_code=ErrorCode.internal_error)
