# file: router.py
import os
from typing import List, Optional,Any, Union,Annotated
from datetime import date
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile,Form,Query
from motor.core import AgnosticDatabase
from fastapi.responses import JSONResponse,FileResponse
from fastapi.encoders import jsonable_encoder
from app.auth.deps import get_current_active_user,get_current_active_superuser
from app.user.models import User
from app.project.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.project.crud import proj
from app.deps import get_db
import pprint
from app.project.models import Project , datetime_now_sec


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
    state: str =Form(None),
    zipcode:Optional[int] = Form(None),
    amount: int= Form(...), 
    duration:Optional[date] =Form(default=datetime_now_sec),
    title: str =Form(...),
    about: Optional[str] =Form(None),
    categories: str  = Form(...),
    story: Optional[str] = Form(None),
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
            state = state,
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
        
        project_id= await proj.create_project(db,user,project_in, picture_bytes)
        project_id=jsonable_encoder(project_id)
        return JSONResponse(status_code=201, content={
            "status": "success",
            "message": "Project with the below id was created successfully",
            "data": project_id
        })
        
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "message": e.detail,
            "data": None
        })
        
    except Exception as e:
        return JSONResponse(status_code=400, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
        


@router.get("/", response_model=List[Project])
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
        
        
@router.get("/number-of-porjects")
async def number_of_projects(
    db: AgnosticDatabase = Depends(get_db),
)->int:
    """_summary_
        this route gives your the number of projects created.
    """
    try:
        
        num_of_projects = await proj.get_number_of_projects(db)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "The number of projects created is:",
            "data": num_of_projects
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
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "message": e.detail,
            "data": None
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


@router.get("/user/project", response_model=List[ProjectOut])
async def get_user_projects(
    db: AgnosticDatabase = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    """Retrieve projects created by the current user"""
    try:
        user_projects = await proj.get_projects_by_user(db, user.id)
        user_projects = jsonable_encoder(user_projects)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "User projects retrieved successfully",
            "data": user_projects
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })


@router.put("/project/update_about")
async def update_about_project(
    project_id: str = Query(description="the project ID", max_length=24),
    about: str = Query(description="update for the about field",max_length=2000),
    user:User =Depends(get_current_active_user),
    db: AgnosticDatabase=Depends(get_db)
):
    
    try:
        project = await proj.update_about(db,project_id,about)
        project =jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "Projects about filed updated successfully retrieved successfully",
                "data": project
            })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 



@router.put("/project/update_story")
async def update_about_project(
    project_id: str = Query(description="the project ID", max_length=24),
    story: str = Query(description="update for the about field",max_length=2000),
    user:User =Depends(get_current_active_user),
    db: AgnosticDatabase=Depends(get_db)
):
    
    try:
        project = await proj.update_story(db,project_id,story)
        project =jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "Projects about filed updated successfully retrieved successfully",
                "data": project
            })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 


@router.put("/project/update_category")
async def update_project_catagory(
    project_id: str = Query(description="the project ID", max_length=24),
    category_id: str =Query(description="the category id", max_length=24),
    # user:User =Depends(get_current_active_user),
    db: AgnosticDatabase=Depends(get_db)
):
    """This route updates the category field of a project, 
    obtain the category id from the project category route
    , use the id to update the category a project created"""
    
    try:
        project = await proj.update_project_category(db,project_id,category_id)
        project =jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
                "status": "success",
                "message": "Projects about filed updated successfully retrieved successfully",
                "data": project
            })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        }) 

@router.get("/filter/category", response_model=List[ProjectOut])
async def filter_projects_by_category(
    category: str = Query(..., description="Category to filter projects by"),
    db: AgnosticDatabase = Depends(get_db),
):
    """Retrieve projects filtered by category"""
    try:
        projects = await proj.get_projects_by_category(db, category)
        projects = jsonable_encoder(projects)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Projects filtered by category retrieved successfully",
            "data": projects
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })
        
 
@router.get("/projects/backings")
async def get_project_backing(
    db: AgnosticDatabase = Depends(get_db),
)->int:
    """Retrieve the total number of backings received by all the projects."""
    try:
        project_backing = await proj.get_number_of_backings(db)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Projects received a total backing of:",
            "data": project_backing
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })                                                                                                            


@router.get("/project/{project_id}", response_model=ProjectOut)
async def get_user_projects(
    project_id =str,
    db: AgnosticDatabase = Depends(get_db),
):
    """Retrieve project with the project_id without , authorising a user,
    this route give you a project when provided with the project id"""
    
    try:
        project = await proj.get_project_without_user(db, project_id)
        project = jsonable_encoder(project)
        return JSONResponse(status_code=200, content={
            "status": "success",
            "message": "Project retrieved successfully",
            "data": project
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
            "data": None
        })


@router.get("/image_or_video/{project_id}")
async def get_project_image(
    project_id: str,
    db: AgnosticDatabase = Depends(get_db)
):
    """Retrieve the image or video of a project by project ID, 
    provide the project id , in the route to receive the image or video"""
    try:
        image_path = await proj.get_project_image_path(db, project_id)
        if not os.path.exists(image_path):
            return JSONResponse(status_code=404, content={
                "status": "error",
                "message": "Image not found",
                "data": None
            })
        return FileResponse(image_path)
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