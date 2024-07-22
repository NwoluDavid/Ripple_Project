# file: schemas.py

from pydantic import BaseModel, Field
from odmantic import ObjectId
from datetime import datetime , date
from typing import Optional

class ProjectCreate(BaseModel):
    name: str = Field(default =None , description = "The name of user creating the project",example ="JohnDoe", min_length =8, max_length =64)
    address: str =Field(default =None , description = "The addres of the user",example ="Lagos,Nigeria", min_length =8, max_length =64)
    zipcode: int =Field(default =None , description ="provide the zip code of the user" , example ="40213", gt=5)
    amount: int=Field(default =None , description ="the user provides the amount he/she wants to raise" , example ="10000",)
    duration: date
    title: str=Field(default =None , description = "The user states the title of the project",example ="Electric Motor", min_length =8, max_length =64)
    about: str=Field(default =None , description = "The user states what their kickstarted is about",example ="JohnDoe", min_length =8, max_length =600)
    # photo_or_video: Optional[str] =Field(default =None , description = "The name of the video or image file provided by the user",example ="JohnDoe.jpg", min_length =8, max_length =64)
    categories: str=Field(default =None , description = "The user add the categories of his/her project",example ="Design $ tech", max_length =24)
    story: str=Field(default =None , description = "user shares the story of the project",example ="user story", min_length =8, max_length =1000)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    zipcode: Optional[int] = None
    amount: Optional[int] = None
    duration: Optional[datetime] = None
    title: Optional[str] = None
    about: Optional[str] = None
    categories: Optional[str] = None
    story: Optional[str] = None

class ProjectOut(BaseModel):
    id: str
    name: str
    address: str
    zipcode: int
    created: datetime
    modified: datetime
    amount: int
    duration: date
    title: str
    about: str
    picture_or_video: str
    categories: str
    story: str
    user_id: str
