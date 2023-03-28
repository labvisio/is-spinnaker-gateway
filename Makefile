USER := luizcarloscf
IMAGE := is-spinnaker-gateway
PYTHON := python3
SHELL := /bin/bash

help:
	@ echo "Usage:"
	@ echo "make clean-pyc     Remove python files artifacts."
	@ echo "make clean-docker  Clean all stopped containers and build cache."
	@ echo "make clean         clean-pyc and clean-docker."
	@ echo "make image         Build docker image."
	@ echo "make push          Push docker image to dockerhub."
	@ echo "make login         Login on docker (necessary to push image)."
	@ echo "make venv          Create virtual env."
	@ echo "make install       Create virtual env and install all package dependencies."
	@ echo "make build         Rebuild is-spinnaker-gateway package."
	@ echo "make test          Run tests of is-spinnaker-gateway package using pytest."
	@ echo "make lint          Run linter on project."
	@ echo "make all           Run install, build, test and lint at once."
	@ echo "make run           Run is-spinnaker-gateway executable."
	@ echo "make build         Run protoc compiler."

clean-pyc:
	@rm -rfv `find . \
		-type d -name __pycache__ \
		-o -type f -name \*.pyc \
		-o -type f -name \*.pyd \
		-o -type f -name \*.pyo \
		-o -type f -name \*.~ \
		-o -type f -name '__pycache__'`

	@rm -rfv \
		*.core \
		*.egg-info \
		*\@is-spinnaker-gateway* \
		.coverage \
		.pytest_cache \
		.tox \
		build \
		dist \
		htmlcov \
		wheelhouse

clean-docker:
	@docker system prune

clean: clean-pyc clean-docker 

image:
	docker build -f etc/docker/Dockerfile -t $(USER)/$(IMAGE):$(VERSION) .

push:
	docker push $(USER)/$(IMAGE):$(VERSION)

login:
	docker login

all: install build test lint

install: venv
	: # Activate venv and install something inside
	@. .venv/bin/activate && (\
      pip3 install .[dev]; \
      pip3 install --upgrade protobuf==3.20.3 \
    )

venv:
	: # Create venv if it doesn't exist
	test -d .venv || python3 -m venv .venv
	@. .venv/bin/activate && (\
      pip3 install --upgrade pip wheel \
    )

build:
	: # determine if we are in venv,
	: # see https://stackoverflow.com/q/1871549
	. .venv/bin/activate && pip -V
	: # rebuild
	@. .venv/bin/activate && (\
    	pip3 install .; \
    	pip3 install --upgrade protobuf==3.20.3 \
	)

test:
	@. .venv/bin/activate && (\
    	pytest tests \
	)

lint:
	@. .venv/bin/activate && (\
    	flake8 is_spinnaker_gateway; \
    	flake8 tests; \
    	flake8 examples; \
	)

run:
	@. .venv/bin/activate && (\
		is-spinnaker-gateway etc/conf/options.json \
	)

proto:
	@protoc -I=. --python_out=. ./is_spinnaker_gateway/conf/options.proto

.PHONY: help clean-pyc clean-docker image push login install venv build test lint all run proto
