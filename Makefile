.ONESHELL:
SHELL=/bin/bash
API_FOLDER=app
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

new-venv:
	if [ ! -d "$(VENV_DIR)" ]; then
		python3 -m venv $(VENV_DIR);
	fi

install-linux-deps:
	sudo apt update && sudo apt install python3-dev graphviz graphviz-dev

pip-install:
	$(PYTHON) -m pip install -U pip
	if ! command -v uv &> /dev/null; then
		$(PYTHON) -m pip install -U uv
	fi
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv pip install -Ur requirements/base.txt
	uv pip install -Ur requirements/dev.txt
	pre-commit autoupdate

install: new-venv install-linux-deps pip-install

ci-install: install-linux-deps pip-install

lint:
	@echo "${BOLD}${YELLOW}pre-commit:${NORMAL}"
	pre-commit autoupdate
	pre-commit run --all-files

test-integration:
	@echo "${BOLD}${YELLOW}Running integration tests:${NORMAL}"
	# ! --dist=loadfile to let Tests are grouped by their containing file.
	# Groups are distributed to available workers as whole units.
	# This guarantees that all tests in a file run in the same worker.
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html#running-tests-across-multiple-cpus
	$(PYTHON) -m pytest tests/integration -n auto --dist=loadfile -s

test-unit:
	@echo "${BOLD}${YELLOW}Running unit tests:${NORMAL}"
	$(PYTHON) -m pytest tests/unit

# ! need to run docker in advance: make run-docker-compose
test: test-integration

run:
	TESTING=true uvicorn ${API_FOLDER}.main:app --reload

run-with-external-db:
	uvicorn ${API_FOLDER}.main:app --reload

run-with-multi-core:
	# ! gunicorn might not be necessary for single core environments
	# (for e.g. K8S pod with 1 core with HPA Horizontol Pod Autoscaling)
	# https://fastapi.tiangolo.com/deployment/docker/#one-process-per-container
	# if multi core used, then workers = 2 * num_cpus + 1 as best practices
	# https://fastapi.tiangolo.com/deployment/server-workers/#gunicorn-with-uvicorn-workers
	gunicorn ${API_FOLDER}.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

run-docker-compose:
	docker compose build && docker compose up -d

dbsqlite:
	sqlite3 db.sqlite3
