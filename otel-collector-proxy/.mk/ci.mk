VERSION ?= latest

##@ CI
.PHONY: ci_push
ci_push: ## Executed upon ci push event
	@echo "|||====> Executing make docker_build"
	VERSION=$(VERSION) make docker_build
	@echo "|||====> docker_build Done."
	@echo "|||====> Executing make docker_push"
	VERSION=$(VERSION) make docker_push
	@echo "|||====> docker_push Done."
