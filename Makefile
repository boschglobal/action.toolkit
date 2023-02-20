# SPDX-FileCopyrightText: 2023 Robert Bosch GmbH
#
# SPDX-License-Identifier: Apache-2.0


###############
## Package parameters.
export PACKAGE_VERSION ?= 0.0.1
PACKAGE_DOC_NAME = GitHub Action Python Toolkit
PACKAGE_NAME = action.toolkit


###############
## PyPI parameters.
##	Taken from environment: PYPI_REPO, PYPI_USER, PYPI_TOKEN.
export PYPI_PACKAGE_NAME = $(PACKAGE_NAME)
export TWINE_PASSWORD = $(PYPI_TOKEN)


##############
## Builder Image.
export BUILDER_IMAGE ?= python:3.9-bullseye
ifneq ($(CI), true)
	DOCKER_BUILDER_CMD := docker run -it --rm \
		--env PIP_EXTRA_INDEX_URL=$(PIP_EXTRA_INDEX_URL) \
		--env PACKAGE_VERSION=$(PACKAGE_VERSION) \
		--volume $$(pwd):/tmp/repo \
		--workdir /tmp/repo \
		$(BUILDER_IMAGE)
endif


.PHONY: build do-build install do-test test push clean super-linter

default: build

do-build:
	@echo "Building Python Package:"
	@echo "    PyPI Package Name    : $$PYPI_PACKAGE_NAME"
	@echo "    PyPI Package Version : $$PACKAGE_VERSION"
	mkdir -p dist
	python3 setup.py sdist bdist_wheel
build:
	@${DOCKER_BUILDER_CMD} $(MAKE) do-build

install:
	pip install -e .

do-test: install
	pytest -rx tests
test:
	@${DOCKER_BUILDER_CMD} $(MAKE) do-test

push:
	@echo "Uploading Python Package:"
	@echo "    PyPI Package Name    : $$PYPI_PACKAGE_NAME"
	@echo "    PyPI Package Version : $$PACKAGE_VERSION"
	@echo "    PyPI Repo URL        : $$PYPI_REPO"
	@echo "    PyPI User            : $$PYPI_USER"
	@echo "    PyPI Token           : **** ****" #$$TWINE_PASSWORD"
	twine upload --verbose --disable-progress-bar \
	    --repository-url $$PYPI_REPO \
		--username $$PYPI_USER \
		dist/*

clean:
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./*.egg-info

super-linter:
	docker run --rm --volume $$(pwd):/tmp/lint \
		--env RUN_LOCAL=true \
		--env DEFAULT_BRANCH=main \
		--env IGNORE_GITIGNORED_FILES=true \
		--env VALIDATE_ANSIBLE=false \
		--env VALIDATE_ARM=false \
		--env VALIDATE_BASH=false \
		--env VALIDATE_BASH_EXEC=false \
		--env VALIDATE_CLANG_FORMAT=false \
		--env VALIDATE_CPP=false \
		--env VALIDATE_CSHARP=false \
		--env VALIDATE_DOCKERFILE_HADOLINT=false \
		--env VALIDATE_GO=false \
		--env XXX_VALIDATE_GHERKIN=false \
		--env VALIDATE_GITHUB_ACTIONS=false \
		--env VALIDATE_GITLEAKS=false \
		--env VALIDATE_GOOGLE_JAVA_FORMAT=false \
		--env VALIDATE_GROOVY=false \
		--env VALIDATE_HTML=false \
		--env VALIDATE_JAVA=false \
		--env VALIDATE_JAVASCRIPT_ES=false \
		--env VALIDATE_JAVASCRIPT_STANDARD=false \
		--env VALIDATE_JSCPD=false \
		--env VALIDATE_LUA=false \
		--env XXX_VALIDATE_MARKDOWN=false \
		--env VALIDATE_PYTHON=false \
		--env VALIDATE_PYTHON_BLACK=false \
		--env XXX_VALIDATE_PYTHON_FLAKE8=false \
		--env VALIDATE_PYTHON_ISORT=false \
		--env VALIDATE_PYTHON_MYPY=false \
		--env XXX_VALIDATE_PYTHON_PYLINT=false \
		--env VALIDATE_RUST_2015=false \
		--env VALIDATE_RUST_2018=false \
		--env VALIDATE_RUST_CLIPPY=false \
		--env XXX_VALIDATE_YAML=false \
		github/super-linter:slim-v4
