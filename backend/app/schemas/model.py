from typing import Dict, List

from backend.common import common
from pydantic import BaseModel, Field


class Algorithm(BaseModel):
    algorithm_name: str = Field(..., max_length=255)
    params: List[Dict]


class Model(BaseModel):
    model_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    model_name: str = Field(..., max_length=255)
    model_version: int
    model_algorithm: Algorithm


class CreateModel(BaseModel):
    machine_id: str
    target_dir: str
    algorithm: str
    params: Dict


class CreateContainer(BaseModel):
    model: str
    version: str
    tag_name: str
