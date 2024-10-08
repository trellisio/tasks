from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.services.errors import (
    NoResourceException,
    ResourceExistsException,
    ServiceException,
    ValidationError,
)


def register_handlers(app: FastAPI):
    app.add_exception_handler(ValidationError, service_validation_error_handler)
    app.add_exception_handler(NoResourceException, service_no_resource_error_handler)
    app.add_exception_handler(
        ResourceExistsException, service_resource_exists_error_handler
    )
    app.add_exception_handler(ServiceException, service_base_error_handler)
    app.add_exception_handler(Exception, base_error_handler)


async def service_validation_error_handler(_: Request, exception: ValidationError):
    return JSONResponse(
        status_code=422, content=jsonable_encoder(exception.serialize())
    )


async def service_no_resource_error_handler(_: Request, exception: NoResourceException):
    return JSONResponse(
        status_code=401, content=jsonable_encoder(exception.serialize())
    )


async def service_resource_exists_error_handler(
    _: Request, exception: ResourceExistsException
):
    return JSONResponse(
        status_code=400, content=jsonable_encoder(exception.serialize())
    )


async def service_base_error_handler(_: Request, exception: ServiceException):
    return JSONResponse(
        status_code=400, content=jsonable_encoder(exception.serialize())
    )


async def base_error_handler(_: Request, exception: Exception):
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            {"msg": "Internal Server Error", "detail": str(exception)}
        ),
    )
