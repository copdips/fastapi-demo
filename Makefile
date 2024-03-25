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

test:
	@echo "${BOLD}${YELLOW}Running unit tests:${NORMAL}"
	$(PYTHON) -m pytest

test-integration:
	@echo "${BOLD}${YELLOW}Running integration tests:${NORMAL}"
	$(PYTHON) -m pytest tests/integration --cov-fail-under=95

test-all: test test-integration

run:
	TESTING=true uvicorn ${API_FOLDER}.main:app --reload

run-with-external-db:
	uvicorn ${API_FOLDER}.main:app --reload
