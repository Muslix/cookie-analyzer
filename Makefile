.PHONY: clean install test lint format release

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e .
	pip install -r requirements.txt

test:
	pytest tests/

coverage:
	pytest --cov=cookie_analyzer tests/ --cov-report=term --cov-report=html

lint:
	flake8 cookie_analyzer tests
	pylint cookie_analyzer tests

format:
	black cookie_analyzer tests

release:
	python -m build
	twine check dist/*
	twine upload dist/*