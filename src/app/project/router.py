# file: router.py
import os
from typing import List, Optional,Any, Union,Annotated
from datetime import date
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile,Form
from motor.core import AgnosticDatabase
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.auth.deps import get_current_active_user,get_current_active_superuser
from app.user.models import User
from app.project.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.project.crud import proj
from app.deps import get_db
import pprint
from app.project.models import Project


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)

UPLOAD_DIR = "uploads/projects/"

@router.post("/")
async def create_project(
    *,
    name: str =Form(...),
    address: str =Form(...),
    zipcode: int = Form(...),
    amount: int= Form(...), 
    duration: date =Form(...),
    title: str =Form(...),
    about: str =Form(...),
    categories: str  = Form(...),
    story: str = Form(...),
    db: AgnosticDatabase = Depends(get_db),
    user: User = Depends(get_current_active_user),
    picture_or_video : UploadFile =File(None)
    
):
    """This route is for a user to create a project,
    the user must be a registered user ."""
    
    try:
        picture_bytes = await picture_or_video.read() if picture_or_video else None

        project_in= Project(
            name = name,
            address = address,
            zipcode= zipcode,
            amount= amount, 
            duration = duration,
            title = title,
            about = about,
            categories = categories,
            story = story,
            user_id =user.id,
            picture_or_video =picture_or_video.filename if picture_or_video else None
        )
        
        print(project_in)
        
        project = await proj.create_project(db,user,project_in, picture_bytes)
        project =jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project created successfully",
            "data": project
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
        


@router.get("/", response_model=List[ProjectOut])
async def list_projects(
    db: AgnosticDatabase = Depends(get_db),
):
    try:
        
        projects = await proj.get_list_project(db)
        projects = jsonable_encoder(projects)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Projects retrieved successfully",
            "data": projects
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })        
        
@router.get("/{project_id}", response_model=ProjectOut)
async def read_project(
    project_id: str,
    db: AgnosticDatabase = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    try:
        project = await proj.get_project(db, project_id)
        project = jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project retrieved successfully",
            "data": project
        })
    
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })

@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: AgnosticDatabase = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    try:
        updated_project = await proj.update_project(db,user, project_id, project_in)
        updated_project = jsonable_encoder(updated_project)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project updated successfully",
            "data": updated_project
        })
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "message": e.detail,
            "data": None
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AgnosticDatabase = Depends(get_db),
    user: User = Depends(get_current_active_superuser)
):
    try:
        await proj.delete_project(db, project_id)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project deleted successfully",
            "data": None
        })
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "message": e.detail,
            "data": None
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })

