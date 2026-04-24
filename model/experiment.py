

from typing import Optional

from sqlmodel import Field, SQLModel


class ClusterExperiment(SQLModel, table=True):

    __tablename__ = 't_cluster_experiment'

    id: int = Field(primary_key=True, default=None)
    cluster_num: int  # 聚类数量
    silhouette_score: float  # 轮廓系数
    run_time: float  # 运行时间
