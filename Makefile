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

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -U -r requirements/base.txt
	$(PYTHON) -m pip install -U -r requirements/dev.txt
	pre-commit autoupdate

lint:
	@echo "${BOLD}${YELLOW}pre-commit:${NORMAL}"
	pre-commit run --all-files


test-integration:
	@echo "${BOLD}${YELLOW}Running integration tests:${NORMAL}"
	# ! --dist=loadfile to let Tests are grouped by their containing file.
	# Groups are distributed to available workers as whole units.
	# This guarantees that all tests in a file run in the same worker.
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html#running-tests-across-multiple-cpus
	$(PYTHON) -m pytest tests/integration -n auto --dist=loadfile

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
