from fastapi import APIRouter

from .monitoring import monitoring_routes

router = APIRouter()
v1_router = APIRouter(prefix="/v1")

# monitoring
router.include_router(monitoring_routes.router)

# v1


# main
router.include_router(v1_router)
