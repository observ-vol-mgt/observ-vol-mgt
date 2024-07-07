
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
	echo "building the *builder* image"
	DOCKER_BUILDKIT=1 docker build --build-arg EXECUTE_TESTS=false --progress=plain --target builder-stage --cache-from ${DOCKER_IMAGE_BASE}controller:builder -t ${DOCKER_IMAGE_BASE}controller:builder .
	echo "building the *execute* image"
	DOCKER_BUILDKIT=1 docker build --build-arg EXECUTE_TESTS=false --progress=plain --target execute-stage --cache-from ${DOCKER_IMAGE_BASE}controller:builder -t ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG} .

docker_push: ## push to docker registry
	echo "pushing docker images"
	docker push ${DOCKER_IMAGE_BASE}controller:builder
	docker push ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG}

.PHONY: docker_run_tests
docker_run_tests: ## Execute tests using docker
	DOCKER_BUILDKIT=1 docker pull quay.io/observ-vol-mgt/controller:builder
	DOCKER_BUILDKIT=1 docker build . --progress=plain --build-arg EXECUTE_TESTS=true --cache-from ${DOCKER_IMAGE_BASE}controller:builder --target tests-stage

.PHONY: docker_run_end2end_tests
docker_run_end2end_tests: ## Execute end2end tests using docker
	DOCKER_BUILDKIT=1 docker pull quay.io/observ-vol-mgt/controller:builder
	DOCKER_BUILDKIT=1 docker build . --progress=plain --build-arg EXECUTE_END2END_TESTS=true --cache-from ${DOCKER_IMAGE_BASE}controller:builder --target tests-end2end-stage

.PHONY: docker_run_dev
docker_run_dev: docker_build ## Execute the pipeline synchronously on synthetic data using docker
	docker run --name controller ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG} 

include .mk/development.mk
include .mk/ci.mk