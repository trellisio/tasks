from typing import Annotated, TypedDict

from fastapi import Depends, Header, HTTPException, Query
from kink import di

from app.services.ports.auth import Auth, Jwt


class Pagination(TypedDict):
    skip: int
    limit: int


def pagination(
    *,
    skip: Annotated[int, Query(ge=0)],
    limit: Annotated[int, Query(le=500)],
) -> Pagination:
    return {"skip": skip, "limit": limit}


async def validate_token(
    *,
    auth: Annotated[Auth, Depends(lambda: di[Auth])],
    authorization: Annotated[str, Header()],
) -> Jwt:
    try:
        return await auth.decode(token=authorization)
    except Exception:  # noqa: BLE001
        raise HTTPException(401)  # noqa: B904


async def decode_token(
    *,
    auth: Annotated[Auth, Depends(lambda: di[Auth])],
    authorization: Annotated[str, Header()],
) -> Jwt:
    return await auth.decode(token=authorization, validate=False)


def get_current_user(
    token: Annotated[Jwt, Depends(decode_token)],
) -> str:
    return token.user_id
