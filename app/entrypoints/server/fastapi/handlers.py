from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.services.errors import NoResourceError, ResourceExistsError, ServiceError, ValidationError


def register_handlers(app: FastAPI):
    app.add_exception_handler(ValidationError, service_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(NoResourceError, service_no_resource_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        ResourceExistsError,
        service_resource_exists_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(ServiceError, service_base_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, base_error_handler)


def service_validation_error_handler(_: Request, exception: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(exception.serialize()),
    )


def service_no_resource_error_handler(_: Request, exception: NoResourceError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=jsonable_encoder(exception.serialize()),
    )


def service_resource_exists_error_handler(
    _: Request,
    exception: ResourceExistsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(exception.serialize()),
    )


def service_base_error_handler(_: Request, exception: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(exception.serialize()),
    )


def base_error_handler(_: Request, exception: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            {"msg": "Internal Server Error", "detail": str(exception)},
        ),
    )
