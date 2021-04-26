.DEFAULT_GOAL := all

.PHONY: all
all: check test

.PHONY: install-packages
install-packages:
	pip3 install --upgrade \
	  -r dev-requirements.txt \
	  -r requirements.txt \
	  -r test/requirements.txt

.PHONY: check
check: lint typecheck

.PHONY: lint
lint:
	flake8 .

.PHONY: typecheck
typecheck:
	mypy .

.PHONY: test
test: unittest

.PHONY: unittest
unittest:
	python3 -m unittest

.PHONY: run
run:
	python3 elementary_cellular_automaton.py
