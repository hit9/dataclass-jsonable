lint:
	black --check dataclass_jsonable
	isort --profile black --ca --check dataclass_jsonable
	mypy dataclass_jsonable
	ruff check dataclass_jsonable
clean:
	rm -rf dist build *egg-info

build: clean
	python setup.py sdist

upload: build
	twine upload --repository pypi dist/*
