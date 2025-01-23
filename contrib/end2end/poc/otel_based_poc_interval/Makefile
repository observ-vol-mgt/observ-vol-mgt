
# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ POC Demo
start: cleanup_artifacts ## Starts the POC
	make compose_up

perform_analysis: ## Performs observability data analysis
	curl -X POST http://127.0.0.1:5010/api/v1/analyze

delete_configuration: ## Deletes the processors configurations
	curl -X DELETE "127.0.0.1:5010/api/v1/processor_config/east" -H "Content-Type: application/json"
	curl -X DELETE "127.0.0.1:5010/api/v1/processor_config/west" -H "Content-Type: application/json"

end: ## Ends the POC
	make compose_down

##@ POC Development
compose_up: ## Docker compose up
	docker compose -f docker-compose-otel.yml up -d

compose_down: ## Docker compose down
	docker compose -f docker-compose-otel.yml down

stop_controller: ## Stop controller container
	docker compose -f docker-compose-otel.yml stop controller

cleanup_artifacts: compose_down ## Cleanup compose artifacts ( prometheus, thanos and manager data)
	-sudo rm -R thanos_data

	-docker volume rm otel_based_poc_manager_volume
	-docker volume rm otel_based_poc_ruler-shared-data
	-docker volume rm otel_based_poc_east_collector_shared_volume
	-docker volume rm otel_based_poc_west_collector_shared_volume

clean_docker_images: compose_down ## Delete local docker images
	-docker rmi quay.io/observ-vol-mgt/controller
	-docker rmi quay.io/observ-vol-mgt/metricgen
	-docker rmi quay.io/observ-vol-mgt/manager
	-docker rmi quay.io/observ-vol-mgt/ruler_config
	-docker rmi quay.io/observ-vol-mgt/pmf_processor

##@ visualize
.PHONY: show_thanos
show_thanos: ## Show the thanos endpoint (:19192)
	-@chrome --new-window http://127.0.0.1:19192/ &

.PHONY: show_controller
show_controller: ## Show the controller endpoint (:5000)
	-@chrome --new-window http://127.0.0.1:5000/ &
