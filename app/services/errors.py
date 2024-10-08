from typing import TypedDict


class Detail(TypedDict):
    msg: str
    field: str | None


class ServiceException(Exception):
    msg: str
    detail: list[Detail] | None

    def __init__(self, msg: str, detail: list[Detail] | None = None):
        super().__init__(msg)
        self.msg = msg
        self.detail = detail

    def serialize(self):
        payload: dict[str, str | list[Detail]] = {"msg": self.msg}
        if self.detail:
            payload["detail"] = self.detail
        return payload


class NoResourceException(ServiceException):
    def __init__(self, msg: str = "Resource does not exist"):
        super().__init__(msg)


class ResourceExistsException(ServiceException):
    def __init__(self, msg: str = "Resource exists"):
        super().__init__(msg)


class ValidationError(ServiceException):
    def __init__(self, detail: list[Detail], msg: str = "Invalid parameters passed"):
        super().__init__(msg, detail)
