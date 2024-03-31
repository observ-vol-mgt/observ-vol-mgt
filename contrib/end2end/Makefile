.PHONY: help
help: ## Displays help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n"} /^[a-z0-9A-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: up
up: ## Bootstraps a docker-compose setup for local development/demo
	docker-compose up -d --build

.PHONY: restart
restart: ## Rebuilds and restarts the container without building the binary
	docker-compose up -d --build

.PHONY: down
down: ## Brings down the docker-compose setup
	docker-compose down
