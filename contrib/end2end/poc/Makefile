
# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

compose_up: ## Docker compose up
	docker compose -f docker-compose-quay.yml up -d

compose_down: ## Docker compose down
	docker compose -f docker-compose-quay.yml down

stop_controller: ## Stop controller container
	docker compose -f docker-compose-quay.yml stop controller

cleanup: compose_down ## Complete cleanup
	-sudo rm -R prometheus_data1
	-sudo rm -R prometheus_data2
	-sudo rm -R thanos_data
	-docker volume rm poc_manager_volume
	-docker volume rm poc_shared-data

##@ visualize
show_thanos: ## Show the thanos endpoint (:19192)
	chrome --new-window http://127.0.0.1:19192/

show_controller: ## Show the controller endpoint (:5000)
	chrome --new-window http://127.0.0.1:5000/
