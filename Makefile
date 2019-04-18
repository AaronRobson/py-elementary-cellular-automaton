.PHONY: check
check:
	flake8 .

.PHONY: test
test:
	python3 -m unittest
