import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.errors import error_response
from app.api.routes.tasks import router as tasks_router
from app.db.database import engine

app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=404,
        code="not_found",
        message="Resource not found",
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details=exc.errors(),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=500,
        code="internal_server_error",
        message="An unexpected error occurred",
    )


app.include_router(tasks_router)


@app.get("/")
def root():
    return {
        "message": "CRM backend is running",
    }


@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }