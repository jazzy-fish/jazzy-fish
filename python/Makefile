SHELL := /bin/bash

.PHONY: clean
clean:
	@echo Cleaning up builds and caches...
	@rm -rf {out,dist,build}
	@find . -type d -path ./venv -prune -o -name ".pytest_cache" -print -exec rm -rf {} \;
	@find . -type d -path ./venv -prune -o -name "__pycache__" -print -exec rm -rf {} \;
	@find . -type d -path ./venv -prune -o -name "*.egg-info" -print -exec rm -rf {} \;


.PHONY: clean-venv
clean-venv:
	scripts/delete-venv.bash

.PHONY: recreate-venv
recreate-venv:
	@scripts/create-venv.bash

.PHONY: venv
venv:
	@echo "source venv/bin/activate"

.PHONY: install
install:
	@pip install '.[dev]'
	@pip install -e .

.PHONY: build
build:
	@pip install '.[dev]'
	@python setup.py sdist bdist_wheel
	@check-manifest --ignore "wordlists/*/*,scripts/*,.pypirc"

.PHONY: publish-test
publish-test: build
	@echo "Publishing to test repo..."
	@TWINE_PASSWORD=$(TESTPYPI_PASSWORD) twine upload --repository-url https://test.pypi.org/legacy/ dist/\*

.PHONY: publish
publish: build
	@echo "Publishing to PyPI..."
	@TWINE_PASSWORD=$(PYPI_PASSWORD) twine upload dist/\*

.PHONY: publish-verify
publish-verify:
	@echo "Verifying PyPI package..."
	@scripts/verify-publish.bash

show-stats:
	@echo
	@echo "1/millisecond:"
	find out/processed -name 'stats*' -exec grep 'Result: ' {} \; | grep '1/ms' | sort
	@echo
	@echo "1/second:"
	find out/processed -name 'stats*' -exec grep 'Result: ' {} \; | grep '1/s' | sort

store-stats:
	scripts/output-wordlist.bash
	$(MAKE) show-stats | tee -a ../docs/comparison.txt
