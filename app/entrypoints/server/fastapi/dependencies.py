from typing import Annotated, TypedDict

from fastapi import Query


class Pagination(TypedDict):
    skip: int
    limit: int


def pagination(
    *,
    skip: Annotated[int, Query(ge=0)],
    limit: Annotated[int, Query(le=500)],
) -> Pagination:
    return {"skip": skip, "limit": limit}
