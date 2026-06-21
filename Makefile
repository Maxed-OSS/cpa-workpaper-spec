.PHONY: install validate test lint clean

install:
	python3 -m pip install -r requirements.txt

# Validate every bundled example against its schema.
validate:
	python3 validator/validate.py --all

# Run the full test suite.
test:
	python3 -m pytest -q

# List the schema names the validator knows about.
schemas:
	python3 validator/validate.py --list-schemas

clean:
	rm -rf .pytest_cache **/__pycache__ __pycache__
