from fastapi import APIRouter

from .task_list_routes import task_list_v1_routes

v1_router = APIRouter(prefix="/v1")

# v1
v1_router.include_router(task_list_v1_routes.router, prefix="/lists")
