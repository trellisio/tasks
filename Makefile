PYFILES=app tests

# Dependencies
shell:
	poetry shell

install:
	poetry install --with entrypoint_fastapi,dev,test,docs

# Formatting
lint:
	ruff check --fix $(PYFILES)

format:
	ruff format $(PYFILES)

check:
	ruff check $(PYFILES)
	ruff format --check $(PYFILES)

scan:
	bandit -r . -lll # Show 3 lines of context

safety:
	safety check

commit-ready: lint format

# Docker
up:
	docker compose -f ./docker-compose.yml build
	docker compose -f ./docker-compose.yml up -d --force-recreate

down:
	docker compose -f ./docker-compose.yml down --remove-orphans

integration: down up
	docker compose -f ./docker-compose.yml up --exit-code-from integration_tests integration_tests

# Testing
unit:
	pytest -vv --capture=tee-sys --asyncio-mode=auto tests/unit/

int:
	./wait-for.sh http://service_name_fastapi:8000/healthz ./wait-for.sh http://keycloak:8080/realms/trellis/.well-known/openid-configuration pytest -vv tests/integration --capture=tee-sys --asyncio-mode=auto

# Git Hooks
pre-commit: check scan unit # execute in .git/hooks