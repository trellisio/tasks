import json
import time
from typing import Awaitable, Callable, Literal

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger

CallNext = Callable[[Request], Awaitable[Response]]


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AddProcessTimeHeader)
    app.add_middleware(AddRequestLogger)


class AddProcessTimeHeader(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(round(process_time, 5))
        return response


class AddRequestLogger(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext):
        try:
            response = await call_next(request)
        except Exception as e:
            payload = {
                "headers": dict(request.headers),
                "params": dict(request.query_params),
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
            }
            self._log_by_color(
                "error",
                f"[{request.method}] {request.url} -- \n{json.dumps(payload, indent=4)}",
                500,
            )
            raise e

        self._log_by_color(
            "info",
            f"[{request.method}] {request.url} {response.status_code} - {response.headers["X-Process-Time"]}",
            response.status_code,
        )
        return response

    def _log_by_color(
        self, log_type: Literal["info", "error"], message: str, status_code: int
    ):
        color = self._get_color(status_code)
        getattr(logger.opt(ansi=True), log_type)(f"<{color}>{message}</{color}>")

    def _get_color(self, status_code: int):
        if status_code < 300:
            return "green"
        if status_code < 500:
            return "yellow"
        return "red"
