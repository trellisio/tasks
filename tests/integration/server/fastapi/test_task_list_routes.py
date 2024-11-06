import os
from typing import Any

import requests


class TestTaskListRouter:
    service_url = os.environ.get("SERVER_URL")

    def test_create_task_list(self) -> None:
        resp = requests.post(
            f"{self.service_url}/v1/lists",
            json={"name": "TODO", "statuses": ["backlog"]},
            timeout=5,
        )
        assert resp.status_code == 201

    def test_create_task(self) -> None:
        resp = requests.post(
            f"{self.service_url}/v1/lists",
            json={"name": "TODO", "statuses": ["backlog"]},
            timeout=5,
        )
        task_list_pk: Any = resp.json()

        resp = requests.post(
            f"{self.service_url}/v1/lists/{task_list_pk.get('pk')}/tasks",
            json={"title": "Something", "status": "backlog"},
            timeout=5,
        )
        assert resp.status_code == 201
