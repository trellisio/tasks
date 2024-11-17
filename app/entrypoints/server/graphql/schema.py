import strawberry

from .v1 import V1Mutation, V1Query


@strawberry.type
class Query:
    v1: V1Query = strawberry.field(resolver=V1Query, description="v1 API")


@strawberry.type
class Mutation:
    v1: V1Mutation = strawberry.field(resolver=V1Mutation, description="v1 API")


schema = strawberry.Schema(query=Query, mutation=Mutation)
