from typing import Annotated, TypedDict

from fastapi import Depends, Header, HTTPException, Query
from kink import di

from app.services.ports.auth import Auth


class Pagination(TypedDict):
    skip: int
    limit: int


def pagination(
    skip: Annotated[int, Query(ge=0)], limit: Annotated[int, Query(le=500)]
) -> Pagination:
    return {"skip": skip, "limit": limit}


async def validate_token(
    auth: Annotated[Auth, Depends(lambda: di[Auth])],
    authorization: Annotated[str, Header()],
):
    try:
        await auth.validate(authorization)
    except Exception:
        raise HTTPException(401)
