from typing import List
from fastapi import APIRouter, Depends,Form
from motor.core import AgnosticDatabase
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.auth.deps import get_current_active_superuser
from app.deps import get_db
from app.user.models import User
from app.project.models import Project
from app.featured.schemas import FeaturedCreate
from app.featured.crud import featured


router = APIRouter(
    prefix="/featured-projects",
    tags=["featured Project"],
)


@router.get("/",response_model =List[Project])
async def get_featured_project(
    db:AgnosticDatabase=Depends(get_db)
):
    try:
        projects =await featured.get_featured_project(db)
        projects =jsonable_encoder(projects)
        return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "featured projects retrived successfully",
                "data": projects
            })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
        
@router.post("/{project_id}")
async def add_to_featured_project(
    project_id:str,
    db:AgnosticDatabase=Depends(get_db),
    user:User=Depends(get_current_active_superuser)
):
    try:
        featured_project =FeaturedCreate(project_id = project_id)
    
        result =await featured.add_to_featured_collection(db,featured_project)
        result =jsonable_encoder(result)
        return JSONResponse(status_code=201, content={
                "status": "success",
                "message": "project added to featured project was successfully",
                "data": result
            })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
        

@router.delete("/{project_id}")
async def add_to_featured_project(
    project_id:str,
    db:AgnosticDatabase=Depends(get_db),
    user:User=Depends(get_current_active_superuser)
):
    try:
    
        result =await featured.remove_featured_project(db,project_id)
        if result ==1:
            return JSONResponse(status_code=200, content={
                    "status": "success",
                    "message": "featured project deleted successfully",
                    "data": []
                })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })