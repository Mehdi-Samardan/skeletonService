from pydantic import BaseModel
from typing import List


class SkeletonRequest(BaseModel):
    layouts: List[str]
    templates: List[str]
