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

install_requirements:
	@pip install -q -r requirements.txt

##@ Docs
build_and_deploy_docs: install_requirements ## Build and deploy the project documentation
	-git branch -D gh-pages
	-rm -r ../site
	mkdocs build --clean
	-rm -r ../site/contrib/fetch-offline-data/instana/demo-eu/
	-rm -r ../site/controller/metadata_classification/data/few_shot_pretrained_model
	ghp-import --no-history ../site
	git push -f origin gh-pages

show_docs: install_requirements ## Serve the project documentation
	mkdocs serve

##@ Docker
build_docker_images: build_controller_docker_image build_manager_docker_image build_processor_docker_image ## Build docker images
push_docker_images: push_controller_docker_image push_manager_docker_image push_processor_docker_image ## Push docker images


build_controller_docker_image:
	echo "building controller docker images"
	cd controller; \
	DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
	DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
	DOCKER_TAG=${DOCKER_TAG}; \
	make docker_build

push_controller_docker_image:
	echo "pushing controller docker images"
	cd controller; \
	DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
	DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
	DOCKER_TAG=${DOCKER_TAG}; \
	make docker_push

build_manager_docker_image:
	echo "building the manager docker images"
	DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
        DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
        DOCKER_TAG=${DOCKER_TAG}; \
	cd manager/configurator; \
        make docker_build; \
	cd ../alertmanager; \
	make docker_build

push_manager_docker_image:
	echo "pushing the manager docker images"
	DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
        DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
        DOCKER_TAG=${DOCKER_TAG}; \
	cd manager/configurator; \
        make docker_push; \
	cd ../alertmanager; \
	make docker_push

build_processor_docker_image:
	echo "building the processor docker image"
	cd processor; \
        DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
        DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
        DOCKER_TAG=${DOCKER_TAG}; \
        make docker_build

push_processor_docker_image:
	echo "building the processor docker image"
	cd processor; \
        DOCKER_IMAGE_ORG=${DOCKER_IMAGE_BASE}; \
        DOCKER_IMAGE_BASE=${DOCKER_IMAGE_BASE}; \
        DOCKER_TAG=${DOCKER_TAG}; \
        make docker_push

##@ CI
.PHONY: ci_push
ci_push: ## Executed upon ci push (merge) event
	@echo "|||====> Building the project docs"
	make build_and_deploy_docs
	@echo "|||====> Done building project docs."

