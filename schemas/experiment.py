

from typing import Optional

from pydantic import BaseModel


class ClusterExperimentCreateSchema(BaseModel):

    cluster_num: int


class ClusterExperimentQuerySchema(BaseModel):

    cluster_num: int
    