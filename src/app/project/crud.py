from typing import List, Optional,Any
from fastapi.exceptions import HTTPException
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.project.models import Project
from app.db.base import CRUDBase
from app.project.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.user.models import User

import uuid
import os
import pprint

UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):

    async def create_project(self, db: AgnosticDatabase, user:User,project_in:Project, picture_or_video:Optional[bytes]=None) -> Any:
        project_collection = db.project
        
        db_obj=project_in.dict()
        
        if picture_or_video:
            picture_or_video_filename = f"{uuid.uuid4()}_{project_in.picture_or_video}"
            picture_or_video_path = os.path.join(UPLOAD_DIRECTORY, picture_or_video_filename)
            with open(picture_or_video_path, "wb") as buffer:
                buffer.write(picture_or_video)
            db_obj["picture_or_video"] = picture_or_video_path
        
        print(db_obj)
        
        result = await project_collection.insert_one(db_obj)
        result =str(result.inserted_id)
        print(result)
        return result
    
    async def get_list_project(self, db: AgnosticDatabase)->List[ProjectOut]:
        project_collection = db.project
        
        result = project_collection.find()
        num_doc =0
        project_list=[]
        async for document in result:
            num_doc +=1
            
            document["id"]=str(document["_id"])
            del[document["_id"]]
            
            document["user_id"]=str(document["user_id"])
            
            project_list.append(ProjectOut(**document))
        
        print(num_doc)
        
        return project_list    
    
    async def get_project(self, db: AgnosticDatabase, project_id: str) -> Project:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project["id"]=project["_id"]
        del[project["_id"]]
        return Project(**project)
    

    async def get_project_without_user(self, db: AgnosticDatabase, project_id: str) -> Project:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project["id"]=project["_id"]
        del[project["_id"]]
        return Project(**project)
    
    
    async def get_projects_by_user(self, db: AgnosticDatabase, user_id: str) -> List[ProjectOut]:
        project_collection = db.project

        result = project_collection.find({"user_id": ObjectId(user_id)})
        project_list = []
        async for document in result:
            document["id"] = str(document["_id"])
            del document["_id"]

            document["user_id"] = str(document["user_id"])

            project_list.append(ProjectOut(**document))

        return project_list

    async def update_project(self, db: AgnosticDatabase, user:User, project_id: str, project_in: ProjectUpdate) -> Project:
        
        project_collection = db.project
        update_data = {k: v for k, v in project_in.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        #the project document before updating it
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        
        pprint.pprint(project)
        
        if str(project["user_id"]) != str(user.id):
            
            raise HTTPException(status_code =400, detail ="this project does not belong to this user")
        
        await project_collection.update_one({"_id": ObjectId(project_id)}, {"$set": update_data})
        updated_project = await project_collection.find_one({"_id": ObjectId(project_id)})
        
        pprint.pprint(updated_project)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found after update")
        
        # converting bson objectId to string.
        updated_project["id"] =updated_project["_id"]
        del[updated_project["_id"]]
        
        updated_project=Project(**updated_project)
        
        return updated_project

    async def delete_project(self, db: AgnosticDatabase, project_id: str) -> None:
        project_collection = db.project
        result = await project_collection.delete_one({"_id":ObjectId(project_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
    async def get_project_image_path(self, db: AgnosticDatabase, project_id: str) -> str:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project or not project.get("picture_or_video"):
            raise HTTPException(status_code=404, detail="Project or image not found")
        return project["picture_or_video"]


    async def get_projects_by_category(self, db: AgnosticDatabase, category: str) -> List[ProjectOut]:
        
        
        category_collection =db.projectcategories
        project_collection = db.project

        cat =category_collection.find_one(ObjectId(category))
        
        if not cat:
            raise HTTPException(status_code =400, detail ="the category provided is not valid")
        
        result = project_collection.find({"categories": category})
        project_list = []
        async for document in result:
            document["id"] = str(document["_id"])
            del document["_id"]

            document["user_id"] = str(document["user_id"])

            project_list.append(ProjectOut(**document))

        return project_list



proj = CRUDProject(Project)
