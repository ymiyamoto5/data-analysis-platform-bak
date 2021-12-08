from pydantic import BaseModel, Field


class DataRecorderBase(BaseModel):
    processed_dir_path: str
