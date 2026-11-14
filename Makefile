.ONESHELL:
SHELL=/bin/bash
VENV_NAME := $(shell [ -d venv ] && echo venv || echo .venv)
VENV_DIR=${VENV_NAME}
PYTHON=$(shell if [ -d $(VENV_DIR) ]; then echo $(VENV_DIR)/bin/python; else echo python; fi)

ifneq (,$(findstring xterm,${TERM}))
	BOLD	:= $(shell tput -Txterm bold)
	RED	:= $(shell tput -Txterm setaf 1)
	GREEN	:= $(shell tput -Txterm setaf 2)
	YELLOW	:= $(shell tput -Txterm setaf 3)
	NORMAL	:= $(shell tput -Txterm sgr0)
endif

venv:
	# python version comes from .python-version
	uv venv --allow-existing

install-linux-deps:
	sudo apt update && sudo apt install python3-dev graphviz graphviz-dev clang

uv-sync: venv
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv sync --frozen
	uv run pre-commit autoupdate

uv-sync-dev: venv
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv sync --frozen --all-extras --all-groups

uv-update:
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv sync --upgrade --all-extras --all-groups

install: install-linux-deps uv-sync-dev

ci-install: install-linux-deps venv
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv sync --locked --all-extras --all-groups

lint:
	. $(VENV_DIR)/bin/activate
	@echo "${BOLD}${YELLOW}pre-commit:${NORMAL}"
	# staged files are included: `git ls-files -m` is empty once everything is staged,
	# which silently skipped every hook.
	uv run pre-commit run --files $$( { git diff --cached --name-only --diff-filter=ACMR; git ls-files -m -o --exclude-standard; } | sort -u )

test-integration:
	@echo "${BOLD}${YELLOW}Running integration tests for both app layouts:${NORMAL}"
# ! the client fixture is parametrized over both apps, so every test runs twice.
# ! --dist=loadfile to let Tests are grouped by their containing file.
# Groups are distributed to available workers as whole units.
# This guarantees that all tests in a file run in the same worker.
# https://pytest-xdist.readthedocs.io/en/stable/distribution.html#running-tests-across-multiple-cpus
	uv run pytest tests/integration -n auto --dist=loadfile -s

test: test-integration

run-app-layer-based:
	TESTING=true uvicorn app_layer_based_sqlmodel.main:app --reload

run-app-domain-based:
	TESTING=true uvicorn app_domain_based_sqlalchemy.main:app --reload

# ! the deployment-mode targets below default to the domain-based layout,
# ! the same layout the Docker image runs (see the Dockerfile CMD).
run-with-external-db:
	uvicorn app_domain_based_sqlalchemy.main:app --reload

run-with-multi-core:
# ! gunicorn might not be necessary for single core environments
# (for e.g. K8S pod with 1 core with HPA Horizontol Pod Autoscaling)
# https://fastapi.tiangolo.com/deployment/docker/#one-process-per-container
# if multi core used, then workers = 2 * num_cpus + 1 as best practices
# https://fastapi.tiangolo.com/deployment/server-workers/#gunicorn-with-uvicorn-workers
	gunicorn app_domain_based_sqlalchemy.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

run-docker-compose:
	docker compose build && docker compose up -d

show-docker-compose-ps:
	docker compose ps -a --format "table {{.Name}}\t{{.Image}}\t{{.State}}\t{{.Status}}"

dbsqlite:
	sqlite3 db.sqlite3
