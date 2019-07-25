#
# == Paths & Directories ==
#

VENV_DIR := .virtualenv

PYTHON3                    := $(shell command -v python3 2> /dev/null)
PYTHON_REQUIREMENTS        := requirements.txt
PYTHON_FROZEN_REQUIREMENTS := requirements.frozen.txt

#
# == Configuration ==
#

UNAME := $(shell uname)

#
# == Commands ==
#

PIP        := $(VENV_DIR)/bin/pip
PYTEST     := $(VENV_DIR)/bin/pytest
FLAKE8     := $(VENV_DIR)/bin/flake8
MYPY       := $(VENV_DIR)/bin/mypy

#
# == Targets ==
#

default: dependencies

freeze:
	$(PIP) freeze > $(PYTHON_FROZEN_REQUIREMENTS)

dependencies: $(VENV_DIR)
	$(PIP) install wheel
ifdef UNFREEZE
	 $(PIP) install -r $(PYTHON_REQUIREMENTS)
else
	$(PIP) install -r $(PYTHON_FROZEN_REQUIREMENTS)
endif

$(VENV_DIR):
	$(PYTHON3) -m venv --prompt='hashwars' $(VENV_DIR)

lint:
	-$(FLAKE8) hashwars
	-$(MYPY) hashwars/

clean:
	find hashwars test -name '*.pyc' -delete
	find hashwars test -name '__pycache__' -delete

test:
	$(PYTEST)

.PHONY: test
