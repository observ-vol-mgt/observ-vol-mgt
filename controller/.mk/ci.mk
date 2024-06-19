##@ CI
.PHONY: ci_pull_request
ci_pull_request: ## Executed upon ci pull_request event
	@echo "|||====> Executing make Lint"
	make lint
	@echo "|||====> Lint Done."
	@echo "|||====> Executing make docker_run_tests"
	make docker_run_tests
	@echo "|||====> docker_run_tests Done."
	@echo "|||====> Executing make docker_build"

.PHONY: ci_push
ci_push: ci_pull_request ## Executed upon ci push (merge) event
	@echo "|||====> Executing make docker_build"
	make docker_build
	@echo "|||====> docker_build Done."
	@echo "|||====> Executing make docker_push"
	make docker_push
	@echo "|||====> docker_push Done."
