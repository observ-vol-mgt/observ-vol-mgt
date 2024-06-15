
VERSION ?= latest
BUILD_DATE := $(shell date +%Y-%m-%d\ %H:%M)
DOCKER_IMAGE_ORG ?= observ-vol-mgt
DOCKER_IMAGE_BASE ?= quay.io/$(DOCKER_IMAGE_ORG)/
DOCKER_TAG ?= ${VERSION}


# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install_requirements:
	@pip install -q -r requirements.txt

##@ Docker
docker_build: ## build to container
	echo "building docker images"
	DOCKER_BUILDKIT=1 docker build --build-arg EXECUTE_TESTS=false --progress=plain --target builder-stage --cache-from ${DOCKER_IMAGE_BASE}controller:builder -t ${DOCKER_IMAGE_BASE}controller:builder .
	DOCKER_BUILDKIT=1 docker build --build-arg EXECUTE_TESTS=false --progress=plain --target execute-stage --cache-from ${DOCKER_IMAGE_BASE}controller:builder -t ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG} .

docker_push: ## push to docker registry
	echo "pushing docker images"
	docker push ${DOCKER_IMAGE_BASE}controller:builder
	docker push ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG}

.PHONY: docker_run_tests
docker_run_tests: ## Execute tests using docker
	DOCKER_BUILDKIT=1 docker build . --progress=plain --build-arg EXECUTE_TESTS=true --target tests-stage

.PHONY: docker_run_dev
docker_run_dev: docker_build ## Execute the pipeline synchronously on synthetic data using docker
	docker run --name controller ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG} 

##@ Development
.PHONY: tests
tests: install_requirements ## Execute tests
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .

lint: install_requirements ## Lint the code
	flake8 $(shell find . -name '*.py')

.PHONY: run_dev
run_dev: install_requirements  ## Execute the pipeline synchronously on synthetic data
	python main.py -c config.yaml

.PHONY: run_dev_map_reduce
run_dev_map_reduce: install_requirements  ## Execute the pipeline synchronously on synthetic data
	python main.py -c ../contrib/map_reduce_examples/by_name.yaml

show_docs: install_requirements ## Serve the project documentation
	mkdocs serve

##@ CI

.PHONY: ci_pull_request
ci_pull_request: ## Executed upon ci pull_request event
	@echo "====> Executing make Lint"
	make lint
	@echo "====> Lint Done."
	@echo "====> Executing make docker_run_tests"
	make docker_run_tests
	@echo "====> docker_run_tests Done."

