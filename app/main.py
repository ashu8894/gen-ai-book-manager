from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from pydantic import ValidationError

from app.api.v1.endpoints import router as v1_router

app = FastAPI()

# Mount health check here, globally public
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}


# Mount versioned API
app.include_router(v1_router, prefix="/v1/api")

# Validation Error Handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "message": "Validation failed"
        }
    )

# Custom HTTP Exception Handler
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
