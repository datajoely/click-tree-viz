format:
	$(PYTHON) black ./src/


lint:
	$(PYTHON) pylint ./src/click_tree_viz


flint: format lint

test:
	(rm -rf ./artifacts || true) && mkdir -p artifacts/coverage
	$(PYTHON) pytest --cov=. --cov-report term-missing
	(rm -rf ./artifacts)

