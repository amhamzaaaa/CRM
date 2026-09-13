from fastapi import Request
from fastapi.responses import JSONResponse


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details=None,
) -> JSONResponse:
    request_id = request.headers.get("X-Request-ID", "")

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )