from typing import TypedDict


class Detail(TypedDict):
    msg: str
    field: str | None


class ServiceError(Exception):
    msg: str
    detail: list[Detail] | None

    def __init__(self, *, msg: str, detail: list[Detail] | None = None):
        super().__init__(msg)
        self.msg = msg
        self.detail = detail

    def serialize(self) -> dict[str, str | list[Detail]]:
        payload: dict[str, str | list[Detail]] = {"msg": self.msg}
        if self.detail:
            payload["detail"] = self.detail
        return payload


class NoResourceError(ServiceError):
    def __init__(self, *, msg: str = "Resource does not exist"):
        super().__init__(msg=msg)


class ResourceExistsError(ServiceError):
    def __init__(self, *, msg: str = "Resource exists"):
        super().__init__(msg=msg)


class ValidationError(ServiceError):
    def __init__(self, *, detail: list[Detail], msg: str = "Invalid parameters passed"):
        super().__init__(msg=msg, detail=detail)
