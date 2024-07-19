from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.auth.router import router as auth_router
from app.user.router import router as user_router
from app.config import settings
from app.middlewares.exception import ExceptionHandlerMiddleware
import os
import uvicorn


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description=f"{settings.PROJECT_NAME} API",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            # str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

#Add error  handling middleware
# app.add_middleware(ExceptionHandlerMiddleware)

# Add Routers here from modules
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(user_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    port = int(os.environ.get("PORT"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)