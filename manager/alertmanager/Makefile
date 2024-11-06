
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
	echo "building the manager (alertmanager) => ruler_config docker image"
	docker build --cache-from ${DOCKER_IMAGE_BASE}ruler_config -t ${DOCKER_IMAGE_BASE}ruler_config:${DOCKER_TAG} .

docker_push: ## push to docker registry
	echo "pushing the manager (alertmanager) => ruler_config docker image"
	docker push ${DOCKER_IMAGE_BASE}ruler_config:${DOCKER_TAG}

include .mk/ci.mk
