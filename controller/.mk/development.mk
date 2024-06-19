##@ Development
.PHONY: tests
tests: install_requirements ## Execute tests
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest .

.PHONY: lint
lint: install_requirements ## Lint the code
	flake8 $(shell find . -name '*.py')

.PHONY: run_dev
run_dev: install_requirements  ## Execute the pipeline synchronously on synthetic data
	python main.py -c config.yaml

.PHONY: run_dev_map_reduce
run_dev_map_reduce: install_requirements  ## Execute the pipeline using map reduce (scalability)
	python main.py -c contrib/examples/config_files/map_reduce_examples/by_name.yaml

.PHONY: run_dev_instana
run_dev_instana: install_requirements  ## Execute the pipeline using instana demo data
	python main.py -c contrib/examples/config_files/map_reduce_examples/from_instana.yaml
