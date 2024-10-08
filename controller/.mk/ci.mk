VERSION ?= latest

##@ CI
.PHONY: ci_pull_request
ci_pull_request: ## Executed upon ci pull_request event
	@echo "|||====> Executing make Lint"
	VERSION=$(VERSION) make lint
	@echo "|||====> Lint Done."
	@echo ""
	@echo "|||====> Executing make docker_run_tests"
	VERSION=$(VERSION) make docker_run_tests
	@echo "|||====> docker_run_tests Done."
	@echo ""
	@echo "|||====> Executing make docker_run_end2end_tests"
	VERSION=$(VERSION) make docker_run_end2end_tests
	@echo "|||====> make docker_run_end2end_tests Done."
	@echo ""

.PHONY: ci_push
ci_push: ci_pull_request ## Executed upon ci push event
	@echo "|||====> Executing make docker_build"
	VERSION=$(VERSION) make docker_build
	@echo "|||====> docker_build Done."
	@echo "|||====> Executing make docker_push"
	VERSION=$(VERSION) make docker_push
	@echo "|||====> docker_push Done."
