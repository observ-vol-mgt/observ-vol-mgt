# Set the default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

install_requirements:
	@pip install -q -r requirements.txt

##@ Development
tests: install_requirements ## Execute tests
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .

run_dev: install_requirements ## Execute the pipeline synchronously on synthetic data
	python main.py

feature_extraction_tsfel: install_requirements ## Execute the feature extraction using tsfel
	python feature_extraction/feature_extraction_tsfel.py
	
feature_extraction_tsfresh: install_requirements ## Execute the feature extraction using tsfresh
	python feature_extraction/feature_extraction_tsfresh.py
