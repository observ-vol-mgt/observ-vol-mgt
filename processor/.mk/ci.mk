##@ CI
.PHONY: ci_push
ci_push: ## Executed upon ci push (merge) event
	@echo "|||====> Executing make docker_build"
	make docker_build
	@echo "|||====> docker_build Done."
	@echo "|||====> Executing make docker_push"
	make docker_push
	@echo "|||====> docker_push Done."
