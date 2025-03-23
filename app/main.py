from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.api.endpoints import router
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi import status

app = FastAPI()

app.include_router(router)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation failed"
        }
    )
@app.exception_handler(FastAPIHTTPException)
async def custom_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return JSONResponse(
            status_code=401,
            content={"message": "Not authenticated. Please use username and password to authenticate."}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )