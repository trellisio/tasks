from typing import Annotated

from classy_fastapi import Routable, get, post
from fastapi import Depends
from kink import di, inject

from app.services.user import UserCrudService, UserViewService, dtos

from ..dependencies import Pagination, pagination


@inject()
class UserRoutes(Routable):
    crud_service: UserCrudService
    view_service: UserViewService

    def __init__(self, crud_service: UserCrudService, view_service: UserViewService):
        super().__init__()
        self.crud_service = crud_service
        self.view_service = view_service

    @get("/")
    async def list_users(self, commons: Annotated[Pagination, Depends(pagination)]):
        return await self.view_service.list_users(commons["skip"], commons["limit"])

    @post("/")
    async def create_user(self, create_user: dtos.CreateUser):
        return await self.crud_service.create_user(create_user)


user_routes = di[UserRoutes]
