from fastapi import APIRouter

from .monitoring import monitoring_routes
from .task_list import task_list_routes

router = APIRouter()
v1_router = APIRouter(prefix="/v1")

# monitoring
router.include_router(monitoring_routes.router)

# v1
v1_router.include_router(task_list_routes.router, prefix="/lists")

# main
router.include_router(v1_router)
