from typing import List, Optional, Any
from fastapi.exceptions import HTTPException
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.project.models import Project
from app.db.base import CRUDBase
from app.project.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.user.models import User
import uuid
import os

UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):

    async def create_project(
        self, db: AgnosticDatabase, user: User, project_in: Project, picture_or_video: Optional[bytes] = None
    ) -> Any:
        project_collection = db.project
        db_obj = project_in.dict()

        if picture_or_video:
            picture_or_video_filename = f"{uuid.uuid4()}_{project_in.picture_or_video}"
            picture_or_video_path = os.path.join(UPLOAD_DIRECTORY, picture_or_video_filename)
            with open(picture_or_video_path, "wb") as buffer:
                buffer.write(picture_or_video)
            db_obj["picture_or_video"] = picture_or_video_path

        result = await project_collection.insert_one(db_obj)
        return str(result.inserted_id)

    async def get_list_project(self, db: AgnosticDatabase) -> List[ProjectOut]:
        project_collection = db.project
        result = project_collection.find()
        project_list = []

        async for document in result:
            document["id"] = str(document["_id"])
            del document["_id"]
            document["user_id"] = str(document["user_id"])
            project_list.append(ProjectOut(**document))

        return project_list    

    async def get_project(self, db: AgnosticDatabase, project_id: str) -> Project:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project["id"] = str(project["_id"])
        del project["_id"]
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

    async def update_project(
        self, db: AgnosticDatabase, user: User, project_id: str, project_in: ProjectUpdate
    ) -> Project:
        project_collection = db.project
        update_data = {k: v for k, v in project_in.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided for update")

        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if str(project["user_id"]) != str(user.id):
            raise HTTPException(status_code=400, detail="This project does not belong to this user")

        await project_collection.update_one({"_id": ObjectId(project_id)}, {"$set": update_data})
        updated_project = await project_collection.find_one({"_id": ObjectId(project_id)})

        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found after update")

        updated_project["id"] = str(updated_project["_id"])
        del updated_project["_id"]

        return Project(**updated_project)

    async def delete_project(self, db: AgnosticDatabase, project_id: str) -> None:
        project_collection = db.project
        result = await project_collection.delete_one({"_id": ObjectId(project_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")

    async def get_project_image_path(self, db: AgnosticDatabase, project_id: str) -> str:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project or not project.get("picture_or_video"):
            raise HTTPException(status_code=404, detail="Project or image not found")
        return project["picture_or_video"]

    async def get_projects_by_category(self, db: AgnosticDatabase, category: str) -> List[ProjectOut]:
        category_collection = db.projectcategories
        project_collection = db.project

        cat = await category_collection.find_one({"_id": ObjectId(category)})
        if not cat:
            raise HTTPException(status_code=400, detail="The category provided is not valid")

        result = project_collection.find({"categories": category})
        project_list = []

        async for document in result:
            document["id"] = str(document["_id"])
            del document["_id"]
            document["user_id"] = str(document["user_id"])
            project_list.append(ProjectOut(**document))

        return project_list

    async def update_about(self, db: AgnosticDatabase, project_id: str, about: str) -> Project:
        project_collection = db.project
        document = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not document:
            raise HTTPException(status_code=400, detail="Project not found")

        await project_collection.update_one({"_id": ObjectId(project_id)}, {"$set": {"about": about}})
        updated_project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found after update")
        
        updated_project["id"] = str(updated_project["_id"])
        del updated_project["_id"]

        return Project(**updated_project)

    async def update_story(self, db: AgnosticDatabase, project_id: str, story: str) -> Project:
        project_collection = db.project
        document = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not document:
            raise HTTPException(status_code=400, detail="Project not found")

        await project_collection.update_one({"_id": ObjectId(project_id)}, {"$set": {"story": story}})
        updated_project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found after update")
        
        updated_project["id"] = str(updated_project["_id"])
        del updated_project["_id"]

        return Project(**updated_project)

    async def update_project_category(
        self, db: AgnosticDatabase, project_id: str, category_id: str
    ) -> Project:
        project_collection = db.project
        document = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not document:
            raise HTTPException(status_code=400, detail="Project not found")

        await project_collection.update_one({"_id": ObjectId(project_id)}, {"$set": {"categories": category_id}})
        updated_project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found after update")
        
        updated_project["id"] = str(updated_project["_id"])
        del updated_project["_id"]

        return Project(**updated_project)
    
    async def get_project_without_user(self, db: AgnosticDatabase, project_id: str) -> Project:
        project_collection = db.project
        project = await project_collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project["id"] = str(project["_id"])
        del project["_id"]
        return Project(**project)
    
    async def get_number_of_projects(self, db: AgnosticDatabase) -> int:
        project_collection = db.project
        result = project_collection.find()
        project_list = []

        async for document in result:
            project_list.append(document)
            number_of_projects =len(project_list)
        return number_of_projects
    
    async def get_number_of_backings(self, db: AgnosticDatabase) -> int:
        project_collection = db.project
        result = project_collection.find()
        project_list = []
        async for document in result:
            project_list.append(document["backer"])
            number_of_backing =len(project_list)
        return number_of_backing
     
proj = CRUDProject(Project)
