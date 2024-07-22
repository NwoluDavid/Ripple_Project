# file: crud.py

from typing import List
from fastapi.exceptions import HTTPException
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.project_categories.models import ProjectCategories
from app.db.base import CRUDBase
from app.project_categories.schemas import ProjectCateUpdate, ProjectCreate
import pprint

class CRUDProjectCate(CRUDBase[ProjectCategories, ProjectCreate, ProjectCateUpdate]):

    async def create_project_category(self, db: AgnosticDatabase, obj_in: ProjectCreate) -> ProjectCategories:
        pro_cat_collection = db.projectcategories
        db_obj = ProjectCategories(name=obj_in.name)
        result = await pro_cat_collection.insert_one(db_obj.dict())
        return db_obj

    async def delete_project_category(self, db: AgnosticDatabase, id: str) -> None:
        pro_cat_collection = db.projectcategories
        document ={"_id":ObjectId(id)}
        db_obj = await pro_cat_collection.find_one(document)
        pprint.pprint(db_obj)
        if not db_obj:
            raise HTTPException(status_code=404, detail="Project category not found")
        result = await pro_cat_collection.delete_one(ObjectId(id))
        return result
        

    async def get_project_categories(self, db: AgnosticDatabase) -> List[ProjectCategories]:
        pro_cat_collection = db.projectcategories
        
        result = pro_cat_collection.find()
        
        categories = []
        async for document in result:
            document["id"] = document["_id"]
            del[document["_id"]]
            pprint.pprint(document)
            # document =ProjectCategories(document)
            categories.append(ProjectCategories(**document))
            return  categories
        

procat = CRUDProjectCate(ProjectCategories)
