lint:
	black --check dataclass_jsonable
	isort --profile black --ca --check .
	mypy .
clean:
	rm -rf dist build *egg-info

build: clean
	python setup.py sdist

upload: build
	twine upload --repository pypi dist/*
