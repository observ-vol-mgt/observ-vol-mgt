from flask import Flask, jsonify, request, abort
import requests
import logging
from config import *
import sys
import os

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
            yaml_content = file.read()

        logger.info(f"GET request successful for processor with id {processor_id}")
        return yaml_content, 200, {'Content-Type': 'application/yaml'}

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        abort(500, "An error occurred while processing the request")

if __name__ == '__main__':
    app.run(host=f"{HOST}", port=f"{PORT}", debug=True)

