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
		uv venv $(VENV_DIR);
	fi
	$(PYTHON) -m pip install -U pip
	if ! command -v uv &> /dev/null; then
		$(PYTHON) -m pip install -U uv
	fi


install-linux-deps:
	sudo apt update && sudo apt install python3-dev graphviz graphviz-dev

pip-install: new-venv
	. $(VENV_DIR)/bin/activate
	export UV_DEFAULT_INDEX=$$PIP_INDEX_URL
	uv pip install -Ur requirements/base.txt
	uv pip install -Ur requirements/dev.txt
	uv pip list
	pre-commit autoupdate
	which pip python uv ruff fastapi pre-commit

install: install-linux-deps pip-install

ci-install: install-linux-deps pip-install

lint:
	. $(VENV_DIR)/bin/activate
	@echo "${BOLD}${YELLOW}pre-commit:${NORMAL}"
	pre-commit autoupdate
	pre-commit run --all-files

test-integration:
	@echo "${BOLD}${YELLOW}Running integration tests for app:${NORMAL}"
	# ! --dist=loadfile to let Tests are grouped by their containing file.
	# Groups are distributed to available workers as whole units.
	# This guarantees that all tests in a file run in the same worker.
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html#running-tests-across-multiple-cpus
	$(PYTHON) -m pytest tests/integration -n auto --dist=loadfile -s

test-integration-domain-based:
	@echo "${BOLD}${YELLOW}Running integration tests for app_domain_based:${NORMAL}"
	# ! --dist=loadfile to let Tests are grouped by their containing file.
	# Groups are distributed to available workers as whole units.
	# This guarantees that all tests in a file run in the same worker.
	# https://pytest-xdist.readthedocs.io/en/stable/distribution.html#running-tests-across-multiple-cpus
	$(PYTHON) -m pytest tests_domain_based/integration --cov app_domain_based --cov-append -n auto --dist=loadfile -s

test-unit:
	@echo "${BOLD}${YELLOW}Running unit tests for app:${NORMAL}"
	$(PYTHON) -m pytest tests/unit

test-unit-domain-based:
	@echo "${BOLD}${YELLOW}Running unit tests for app_domain_based:${NORMAL}"
	$(PYTHON) -m pytest tests_domain_based/unit --cov app_domain_based --cov-append

# ! need to run docker in advance: make run-docker-compose
test: test-integration test-integration-domain-based

run:
	TESTING=true uvicorn ${API_FOLDER}.main:app --reload

run-app-domain-based:
	TESTING=true uvicorn ${API_FOLDER}_domain_based.main:app --reload

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

show-docker-compose-ps:
	docker compose ps -a --format "table {{.Name}}\t{{.Image}}\t{{.State}}\t{{.Status}}"

dbsqlite:
	sqlite3 db.sqlite3

run-sqlalchemy-v1:
	TESTING=true uvicorn app_sqlalchemy_v1.main:app --reload
