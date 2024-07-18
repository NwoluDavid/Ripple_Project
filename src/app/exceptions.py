from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder


class BaseException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.message}"


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    formatted_errors = []

    for error in errors:
        formatted_errors.append(
            {"field": error.get("loc")[-1], "message": error.get("msg")}
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "status": "error",
                "data": None,
                "message": "Validation Error",
                "errors": formatted_errors,
            }
        ),
    )