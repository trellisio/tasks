PYFILES=app tests

# Git Hooks
pre-commit: check scan unit # execute in .git/hooks

# Dependencies
shell:
	poetry shell

install: install-tracing-instrumentation
	poetry install --with entrypoint_fastapi,dev,test,docs

install-tracing-instrumentation:
	opentelemetry-bootstrap -a install

# Database
autogenerate:
	export DB_URL=postgresql+asyncpg://user:password@localhost:5432/tasks && \
	alembic -c app/infra/sqlalchemy/alembic.ini revision --autogenerate
	
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
	docker compose -f ./docker-compose.yml --profile test down --remove-orphans

integration: down
	docker compose -f ./docker-compose.yml build
	docker compose -f ./docker-compose.yml --profile test up --force-recreate --exit-code-from integration_tests integration_tests

# Testing
unit:
	pytest -vv --capture=tee-sys --asyncio-mode=auto tests/unit/

int:
	./wait-for.sh http://tasks_fastapi:8000/api/healthz pytest -vv tests/integration --capture=tee-sys --asyncio-mode=auto
