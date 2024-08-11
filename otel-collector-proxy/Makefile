
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

##@ Docker
.PHONY: docker_build
docker_build: ## build to container
	echo "building the container => otel-collector-proxy docker image"
	docker build --cache-from ${DOCKER_IMAGE_BASE}otel_collector_proxy -t ${DOCKER_IMAGE_BASE}otel_collector_proxy:${DOCKER_TAG} .

.PHONY: docker_push
docker_push: ## push to docker registry
	echo "pushing the image => otel-collector-proxy docker image"
	docker push ${DOCKER_IMAGE_BASE}otel_collector_proxy:${DOCKER_TAG}

##@ Development
.PHONY: run
run: ## Execute the code
	python rest_server.py --save-update-path=/tmp/update.txt --processor-file-to-update=/tmp/processors.txt --docker-container-reset-on-update=tmp

.PHONY: tests
tests: ## Execute tests
	-@pip install -y pytest
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .

include .mk/ci.mk
