# from traceback import print_exception

# from fastapi import Request
# from fastapi.responses import JSONResponse
# from starlette.middleware.base import BaseHTTPMiddleware

# class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         try:
#             return await call_next(request)
#         except Exception as e:
#             print_exception(e)
#             return JSONResponse(
#                 status_code=500, 
#                 content={
#                     'error': e.__class__.__name__, 
#                     'messages': e.args
#                 }
#             )


import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as http_exception:
            return JSONResponse(
                status_code=http_exception.status_code,
                content={"error": "Client Error", "message": str(http_exception.detail)},
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
            )
