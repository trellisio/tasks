import os

import requests

from app.entrypoints.server.fastapi.routes.task_list import CreateTaskListOutputDto
from app.services.task_list.dtos import CreateTaskDto, CreateTaskListDto


class TestTaskListRouter:
    service_url = os.environ.get("SERVER_URL")

    def test_create_task_list(self) -> None:
        resp = requests.post(
            f"{self.service_url}/v1/lists",
            CreateTaskListDto(name="TODO", statuses=set("backlog")).model_dump(),
            timeout=5,
        )
        assert resp.status_code == 201

    def test_create_task(self) -> None:
        resp = requests.post(
            f"{self.service_url}/v1/lists",
            CreateTaskListDto(name="TODO", statuses=set("backlog")).model_dump(),
            timeout=5,
        )
        task_list_pk: CreateTaskListOutputDto = resp.json()

        resp = requests.post(
            f"{self.service_url}/v1/lists/{task_list_pk['pk']}",
            CreateTaskDto(title="Something", status="backlog").model_dump(),
            timeout=5,
        )
        assert resp.status_code == 201
