from fastapi import APIRouter

from .monitoring_routes import monitoring_routes
from .v1 import v1_router

router = APIRouter(prefix="/api")

# monitoring
router.include_router(monitoring_routes.router)


# main
router.include_router(v1_router)
