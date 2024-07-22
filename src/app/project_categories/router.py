# file: router.py

from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticDatabase
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.auth.deps import get_current_active_superuser
from app.project_categories.schemas import ProjectCreate, ProjectCateUpdate
from app.project_categories.crud import procat
from app.deps import get_db
from app.user.models import User

router = APIRouter(
    prefix="/project_categories",
    tags=["Project Categories"],
)

@router.post("/", response_model=dict)
async def create_project_category(
    *,
    db: AgnosticDatabase = Depends(get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_active_superuser)
):
    try:
        project_category = await procat.create_project_category(db=db, obj_in=project_in)
        project_category =jsonable_encoder(project_category)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project category created successfully",
            "data": project_category
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })

@router.delete("/{id}")
async def delete_project_category(
    *,
    db: AgnosticDatabase = Depends(get_db),
    id: str,
    current_user: User = Depends(get_current_active_superuser)
):
    try:
        result = await procat.delete_project_category(db=db, id=id)
        if result:
            return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "Project category deleted successfully",
                "data": None
            })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })

@router.get("/", response_model=List)
async def get_project_categories(
    db: AgnosticDatabase = Depends(get_db)
):
    try:
        categories = await procat.get_project_categories(db=db)
        categories = jsonable_encoder(categories)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project categories retrieved successfully",
            "data": [categories]
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
