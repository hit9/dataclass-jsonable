lint:
	black .
	isort .
clean:
	rm -rf dist build *egg-info

build: clean
	python setup.py sdist

upload: build
	twine upload --repository pypi dist/*
