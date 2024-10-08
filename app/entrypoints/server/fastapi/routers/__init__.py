from fastapi import APIRouter, Depends

from ..dependencies import validate_token
from .monitoring import monitoring_routes

router = APIRouter()
v1_router = APIRouter(prefix="/v1", dependencies=[Depends(validate_token)])

# monitoring
router.include_router(monitoring_routes.router)

# v1

# main
router.include_router(v1_router)
