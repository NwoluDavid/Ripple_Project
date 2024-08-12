from typing import List, Any
from fastapi.exceptions import HTTPException
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.featured.models import Featured
from app.featured.schemas import FeaturedCreate,FeatureUpdate
from app.db.base import CRUDBase
from app.project.models import Project


class CRUDFeatured(CRUDBase[Featured,FeaturedCreate,FeatureUpdate]):
    
    async def add_to_featured_collection(self, db:AgnosticDatabase, featured_project:Featured)->Any:
        featured_collection = db.featured
        project_collection = db.project
        
        featured_project =featured_project.dict()
        is_featured = await featured_collection.find_one({"project_id":featured_project["project_id"]})
        if is_featured:
            raise HTTPException(status_code=400, detail ="Project is already a featured project")
        
        project_in = project_collection.find_one({"_id":ObjectId(featured_project["project_id"])})
        if project_in:
            result = await featured_collection.insert_one(featured_project)
            return str(result.inserted_id)
        raise HTTPException(status_code = 404 , detail="Project Not Found")
    
    async def get_featured_project(self, db:AgnosticDatabase)->List[Project]:
        featured_collection = db.featured
        project_collection = db.project
        
        featured_project =[]
        featured = featured_collection.find()
        async for project in featured:
            project_id =project["project_id"]
            project_out =await project_collection.find_one(ObjectId(project_id))
            project_out["id"]=project_out["_id"]
            del[project_out["_id"]]
            featured_project.append(Project(**project_out))
        return featured_project
    
    async def remove_featured_project(self, db:AgnosticDatabase, project_id: str)->Any:
        featured_collection = db.featured
        featured_project =await featured_collection.find_one({"project_id":project_id})
        if featured_project:
            result = await featured_collection.delete_one({"project_id":project_id})
            return result.deleted_count
        raise HTTPException(status_code = 404, detail = "Featured Project Not Found")
    
featured =CRUDFeatured(Featured)