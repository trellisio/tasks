import json
from abc import ABC, abstractmethod
from functools import wraps
from inspect import signature
from typing import Any, ClassVar, Literal, Mapping, Type

from app.config import config

from .cache import Cache


class Query(ABC):
    """Port to query views / list of objects from database
    Impl is a transactionless select stmt
    Port also implements a cache-aside strategy
    """

    _cache: Cache
    _cache_key_prefix: Literal["__port:Query"]
    _ttl: int | None

    _cache_list: ClassVar[list[str]] = []  # List of methods to be cached

    def __init__(self, *, cache: Cache, ttl: int | None = None):
        self._cache = cache
        self._cache_key_prefix = "__port:Query"
        self._ttl = ttl or config.CACHE_TTL
        self._decorate_to_be_cached_methods()

    # Internals
    def _decorate_to_be_cached_methods(self) -> None:
        for name in self._cache_list:
            method = getattr(self, name)

            sig = signature(method)
            parameters = sig.parameters
            keys = list(parameters.keys())

            @wraps(method)
            async def fn(*args, **kwargs):  # noqa: ANN202, ANN002, ANN003
                if len(args) > 1:
                    msg = "use kwargs for query methods so we can cache on parameter values"
                    raise ValueError(
                        msg,
                    )
                cache_key_prefix = f"{self._cache_key_prefix}:{name}"  # noqa: B023
                param_values = [f"{key}:{kwargs.get(key, "<default>")}" for key in keys]  # noqa: B023
                cache_key = f"{cache_key_prefix}:{":".join(param_values)}"

                result = await self._cache.get(cache_key)
                if result:
                    return json.loads(result)

                result = await method(*args, **kwargs)  # noqa: B023
                await self._cache.set(cache_key, json.dumps(result), self._ttl)
                return result

            setattr(self, name, fn)

    # Interface
    @abstractmethod
    async def execute[T](
        self,
        *,
        query: str,
        params: Mapping[str, Any] | None = None,
        serializer: Type[T],  # noqa: FA100
    ) -> list[T]:
        raise NotImplementedError
