# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Deploy k8s resources
up-k8s: 
	sed 's/APP_HOST/${APPHOST}/g' k8s/ingress.tmpl > k8s/k8s-ingress.yml
	- kubectl create namespace ovm
	kubectl apply -f 'k8s/k8s-*'

down-k8s:
	kubectl delete namespace ovm
