.PHONY: install validate test test-js conformance schemas all clean

install:
	python3 -m pip install -r requirements.txt

# Validate every bundled example against its schema (Python validator).
validate:
	python3 validator/validate.py --all

# Run the full Python test suite (schemas, examples, negatives, conformance).
test:
	python3 -m pytest -q

# Install JS deps and run the JavaScript / Ajv test suite.
test-js:
	cd validator-js && npm install && npm test

# Run the shared conformance suite with the reference Python validator.
conformance:
	python3 conformance/run.py -v

# List the schema names the validator knows about.
schemas:
	python3 validator/validate.py --list-schemas

# Run everything (both validators + conformance).
all: validate test conformance test-js

clean:
	rm -rf .pytest_cache **/__pycache__ __pycache__ validator-js/node_modules
