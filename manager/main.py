from flask import Flask, jsonify, request, abort
import requests
import logging
from config import *
import sys
import os
import yaml

app = Flask(__name__)

# Filter variables from config.py that match the pattern 'PROCESSOR_*_URL' to get the URLs for the edge processors
processor_urls = {key: value for key, value in globals().items() if key.endswith('_URL') and key.startswith('PROCESSOR_')}

# Set up logging
log_dir = os.path.dirname(f'{LOG_FILE}')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=f'{LOG_FILE}', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(f"{PROCESSORS_FOLDER}", exist_ok=True)

for key, value in processor_urls.items():
    file_name = f"{key}".split('_URL')[0].split('PROCESSOR_')[1]
    file_path = f"{PROCESSORS_FOLDER}/{file_name}.yaml"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
                pass  # Do nothing, file created and closed immediately

@app.route('/processors/<processor_id>', methods=['GET'])
def get_processor(processor_id):
    logger.debug(f"GET request received for processor with id {processor_id}")
    try:
        file_path = os.path.join(f"{PROCESSORS_FOLDER}", f"{processor_id}.yaml")
        if not os.path.exists(file_path):
            abort(404, f"Processor with id {processor_id} not found")

        with open(file_path, 'r') as file:
            processor_data = yaml.safe_load(file)


        logger.info(f"GET request successful for processor with id {processor_id}")
        return jsonify([processor_data]), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        abort(500, "An error occurred while processing the request")


@app.route('/processors', methods=['GET'])
def get_all_processors():
    try:
        processor_list = []
        # Iterate over all files in the processors folder
        for file_name in os.listdir(PROCESSORS_FOLDER):
            if file_name.endswith(".yaml"):
                file_path = os.path.join(PROCESSORS_FOLDER, file_name)
                with open(file_path, 'r') as file:
                    processor_data = yaml.safe_load(file)
                    processor_list.append(processor_data)

        logger.info("GET request successful for all processors")
        return jsonify(processor_list), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        abort(500, "An error occurred while processing the request")

@app.route('/processors/<processor_id>', methods=['POST'])
def create_processor(processor_id):
    logger.debug(f"CREATE request received for processor with id {processor_id}")
    try:
        processor_data = request.get_data(as_text=True)

        # Validate if the provided data is valid YAML
        try:
            yaml.safe_load(processor_data)
        except Exception as e:
            abort(404, f"Invalid YAML data")

        file_path = os.path.join(f"{PROCESSORS_FOLDER}", f"{processor_id}.yaml")

        if not os.path.exists(file_path):
            abort(404, f"Processor with id {processor_id} not found")

        if os.path.getsize(file_path) > 0:
            logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

        with open(file_path, 'w') as file:
            file.write(processor_data)

        logger.info(f"POST request successful for processor with id {processor_id}")
        return jsonify({"message":"success", "processor_id": processor_id}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating processor: {str(e)}")
        abort(500, "An error occurred while creating the processor")


@app.route('/processors', methods=['POST'])
def create_all_processors():
    logger.debug("CREATE request received for all processors")
    try:
        processor_data = request.get_data(as_text=True)

        # Validate if the provided data is valid YAML
        try:
            yaml.safe_load(processor_data)
        except Exception as e:
            abort(400, "Invalid YAML data")

        # Iterate over all files in the processors folder
        for file_name in os.listdir(PROCESSORS_FOLDER):
            if file_name.endswith(".yaml"):
                file_path = os.path.join(PROCESSORS_FOLDER, file_name)
                with open(file_path, 'w') as file:
                    file.write(processor_data)

        logger.info("POST request successful for all processors")
        return jsonify({"message": "All processors created successfully"}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating all processors: {str(e)}")
        abort(500, "An error occurred while creating all processors")


if __name__ == '__main__':
    app.run(host=f"{HOST}", port=f"{PORT}", debug=True)

