# Set the default target
.DEFAULT_GOAL := help

VERSION ?= latest
BUILD_DATE := $(shell date +%Y-%m-%d\ %H:%M)
DOCKER_IMAGE_ORG ?= observ-vol-mgt
DOCKER_IMAGE_BASE ?= quay.io/$(DOCKER_IMAGE_ORG)/
DOCKER_TAG ?= ${VERSION}

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Docker
build_docker_images: build_controller_docker_image ## Build docker images
push_docker_images: push_controller_docker_image ## Push docker images


build_controller_docker_image:
	echo "building docker images"
	docker build -t ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG} -f contrib/docker/controller/Dockerfile .

push_controller_docker_image:
	docker push ${DOCKER_IMAGE_BASE}controller:${DOCKER_TAG}