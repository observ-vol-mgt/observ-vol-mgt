# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

cleanup: ## Clean the data folder
	sudo rm -R data

##@ Prometheus(edges)+Thanos(hub)
up-prom-thanos: ## Start end-to-end setup with prometheus at the edge and thanos at the center
	docker-compose --file ./docker-compose-prometheus-thanos.yml up --detach --build

down-prom-thanos: ## Brings down the docker-compose setup
	docker-compose --file ./docker-compose-prometheus-thanos.yml down

##@ otel-collector(edges)+Prometheus(hub)
up-otel-prom: ## Start end-to-end setup with otel collector at the edge and prometheus at the center
	docker-compose --file ./docker-compose-otel-prometheus.yml up --detach --build

down-otel-prom: ## Brings down the docker-compose setup
	docker-compose --file ./docker-compose-otel-prometheus.yml down
