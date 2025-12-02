# Makefile

# The default target (what happens if you just type 'make')
all: install test

# Installation: Upgrades pip, installs audit tool, installs app deps
install:
	python -m pip install --upgrade pip setuptools wheel
	pip install pip-audit
	pip install -r requirements.txt

# Testing: Runs pytest
test:
	pytest ./tests

# Auditing: Runs the security audit
audit:
	pip-audit --strict

# Runs audit without strict mode. This is just for logging/display.
# It won't crash the build if it finds something.
audit-report:
	pip-audit

# Clean up: Removes cache files (optional but nice to have)
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache