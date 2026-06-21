import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from api.v1.schemas.responses import ErrorResponse
from api.v1.services.exceptions.base_exceptions import NotFoundException, AlreadyExistsException, \
    BusinessLogicException, AuthException, ValidationException, PermissionDeniedException

logger = logging.getLogger("app")

async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """401 / 403 – authentication or authorisation failure."""
    logger.warning(
        "AUTH_ERROR | %s %s | code=%s | %s",
        request.method, request.url.path, exc.error_code, exc.message,
    )
    return JSONResponse(
        status_code=HTTP_401_UNAUTHORIZED, # TODO: сделать тут что бы могло возвращать еще 403, в зависимости от типа ошибки
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )

async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedException) -> JSONResponse:
    """403 – permission denied."""
    logger.warning(
        "PERMISSION_DENIED | %s %s | code=%s | %s",
        request.method, request.url.path, exc.error_code, exc.message,
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )

async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """400 – domain-level validation failure."""
    logger.warning(
        "VALIDATION_ERROR | %s %s | code=%s | %s",
        request.method, request.url.path, exc.error_code, exc.message,
    )
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )

async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """404 – requested resource does not exist."""
    logger.info(
        "NOT_FOUND | %s %s | code=%s | %s",
        request.method,
        request.url.path,
        exc.error_code,
        exc.message,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )


async def already_exist_exception_handler(request: Request, exc: AlreadyExistsException) -> JSONResponse:
    """409 – resource already exists (duplicate)."""
    logger.info(
        "CONFLICT | %s %s | code=%s | %s",
        request.method,
        request.url.path,
        exc.error_code,
        exc.message,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )


async def business_exception_handler(request: Request, exc: BusinessLogicException) -> JSONResponse:
    """Configurable 4xx – general business-rule violation."""
    logger.warning(
        "BUSINESS_ERROR | %s %s | code=%s | %s",
        request.method, request.url.path, exc.error_code, exc.message)
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(ErrorResponse.of(code=exc.error_code, message=exc.message).model_dump()),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    422 – Pydantic / FastAPI input-validation failure.

    The ``details`` field contains the structured list of field errors so
    clients can highlight specific form fields without parsing the message.
    """
    # Normalise Pydantic v2 error objects to plain dicts for serialisation
    field_errors = [
        {
            "field": " → ".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    logger.info(
        "VALIDATION_ERROR | %s %s | %d field error(s)",
        request.method,
        request.url.path,
        len(field_errors),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(ErrorResponse.of(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=field_errors,
        ).model_dump()),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    500 – true catch-all for any exception that escaped the domain layer.

    Internal details are *never* leaked to the client; the full traceback is
    captured in the structured log for observability.
    """
    logger.critical(
        "UNHANDLED_EXCEPTION | %s %s | type=%s | %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(ErrorResponse.internal().model_dump()),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP_EXCEPTION | %s %s | status=%d | %s",
        request.method, request.url.path, exc.status_code, exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(ErrorResponse.of(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
        ).model_dump()),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Attach all global exception handlers to *app*.

    Order matters: FastAPI resolves handlers by the MRO of the exception
    class.  More-specific subclasses must be registered **before** their
    base classes to ensure they are matched first.
    """
    app.add_exception_handler(AuthException, auth_exception_handler)          # type: ignore[arg-type]
    app.add_exception_handler(NotFoundException, not_found_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AlreadyExistsException, already_exist_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(BusinessLogicException, business_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationException, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(PermissionDeniedException, permission_denied_exception_handler)  # type: ignore[arg-type]

    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]

    app.add_exception_handler(HTTPException, http_exception_handler)          # type: ignore[arg-type]

    app.add_exception_handler(Exception, unhandled_exception_handler)         # type: ignore[arg-type]
