
# Check if off-line data exists, if not download from Google Drive
OFFLINE_DATA_FOLDER := "../contrib/fetch-offline-data/instana/"
OFFLINE_DATA_DOWNLOAD_FOLDER_NAME := "demo-eu/"
GOOGLE_DRIVE_FOLDER_URL := "https://drive.google.com/drive/folders/1etnVorTiYDxVY7XWx_0naaUTMUvYFPXo"

get_offline_data:
	if [ ! -d "$(OFFLINE_DATA_FOLDER)$(OFFLINE_DATA_DOWNLOAD_FOLDER_NAME)" ]; then \
		$(MAKE) download_offline_data; \
	fi

download_offline_data:
	@echo "Directory $(OFFLINE_DATA_FOLDER) does not exist. Downloading files from Google Drive..."
	@pip install gdown > /dev/null 2>&1
	gdown --folder $(GOOGLE_DRIVE_FOLDER_URL) -O $(OFFLINE_DATA_FOLDER)
	@echo "Done."

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
run_dev_instana: install_requirements get_offline_data  ## Execute the pipeline using instana demo data
	python main.py -c contrib/examples/config_files/map_reduce_examples/from_instana.yaml
