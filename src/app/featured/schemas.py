from pydantic import BaseModel, Field
from odmantic import ObjectId
from typing import Optional

class FeaturedCreate(BaseModel):
    project_id: str =Field (default=None, max_length=24)

class FeatureUpdate(FeaturedCreate):
    pass

class FeaturedIn(FeaturedCreate):
    id: Optional[ObjectId]