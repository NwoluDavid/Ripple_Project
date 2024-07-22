from pydantic import BaseModel , Field
from odmantic import ObjectId


class ProjectCreate(BaseModel):
    name: str = Field(default=None, description="this is the project category", example="Design & Tech")

class ProjectCateUpdate(BaseModel):
    name: str = Field(default=None, description="this is the project category", example="Design & Tech")
