from flask import Flask, jsonify, request, abort
import requests
import logging
from config import *
import sys
import os
import yaml
import json

app = Flask(__name__)


# Filter variables from config.py that match the pattern 'PROCESSOR_*_URL' to get the URLs for the edge processors
processor_urls = {key: value for key, value in globals().items() if key.endswith('_URL') and key.startswith('PROCESSOR_')}

# Set up logging
log_dir = os.path.dirname(f'{LOG_FILE}')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=f'{LOG_FILE}', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(f"{PROCESSORS_FOLDER}", exist_ok=True)
processor_ids = []

for key, value in processor_urls.items():
    file_name = f"{key}".split('_URL')[0].split('PROCESSOR_')[1]
    file_path = f"{PROCESSORS_FOLDER}/{file_name}.yaml"

    if file_name not in processor_ids:
        processor_ids.append(file_name)
    else:
        logger.error(f"Duplicate URL provided for processor with id {processor_id}, we will be using the previously specified URL")
        continue
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
                pass  # Do nothing, file created and closed immediately

@app.route('/processors/<processor_id>', methods=['GET'])
def get_processor(processor_id):
    logger.debug(f"GET request received for processor with id {processor_id}")
    try:
        file_path = os.path.join(f"{PROCESSORS_FOLDER}", f"{processor_id}.yaml")
        if not os.path.exists(file_path):
            return {"message":f"Processor with id {processor_id} not found"}, 404

        with open(file_path, 'r') as file:
            processor_data = yaml.safe_load(file)

        logger.info(f"GET request successful for processor with id {processor_id}")
        return jsonify(processor_data), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        abort(500, "An error occurred while processing the request")

@app.route('/processors', methods=['GET'])
def get_all_processors():
    try:
        processor_list = []
        for processor_id in processor_ids:
            file_name = processor_id + ".yaml"
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
            processor_data_yaml = yaml.safe_load(processor_data)
        except Exception as e:
            logger.error("Invalid yaml data")
            return {"message":"Invalid YAML data"}, 400

        file_path = os.path.join(f"{PROCESSORS_FOLDER}", f"{processor_id}.yaml")
        if not os.path.exists(file_path):
            return {"message":f"Processor with id {processor_id} not found"}, 404
        if os.path.getsize(file_path) > 0:
            logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

        # ------------------------------------------------------------------------------
        # communicate the new dag to the edge processor
        response = requests.post(processor_urls["PROCESSOR_"+processor_id+"_URL"]+PROCESSOR_CREATE_SUFFIX, processor_data_yaml)
        status_code = response.status_code
        if status_code not in [200, 201]:
            logger.error(f"Create DAG request for processor with id {processor_id} failed", response)
            return response.json(), status_code
        # ------------------------------------------------------------------------------


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
    success_list = []
    try:
        processor_data = request.get_data(as_text=True)

        # Validate if the provided data is valid YAML
        try:
            processor_data_yaml = yaml.safe_load(processor_data)
        except Exception as e:
            logger.error("Invalid yaml data")
            return {"message":"Invalid YAML data", "successfully_created": success_list}, 400

        for processor_id in processor_ids:
            file_name = processor_id + ".yaml"
            file_path = os.path.join(PROCESSORS_FOLDER, file_name)

            if not os.path.exists(file_path):
                return {"message":f"Processor with id {processor_id} not found", "successfully_created": success_list}, 404
            if os.path.getsize(file_path) > 0:
                logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

            # ------------------------------------------------------------------------------
            # communicate the new dag to the edge processor
            response = requests.post(processor_urls["PROCESSOR_"+processor_id+"_URL"]+PROCESSOR_CREATE_SUFFIX, processor_data_yaml)
            status_code = response.status_code
            if status_code not in [200, 201]:
                logger.error(f"Create DAG request for processor with id {processor_id} failed", response)
                return {"message" : json.dumps(response.json()), "successfully_created": success_list}, status_code
            # ------------------------------------------------------------------------------

            with open(file_path, 'w') as file:
                file.write(processor_data)

            success_list.append(processor_id)

        logger.info("POST request successful for processors : ", success_list)
        return jsonify({"message": "Create All request completed", "successfully_created": success_list}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating all processors: {str(e)}")
        return {"message" : "An error occurred while creating all processors", "successfully_created": success_list}, 500


@app.route('/processors/<processor_id>', methods=['DELETE'])
def delete_processor(processor_id):
    logger.debug(f"DELETE request received for processor with id {processor_id}")
    try:
        file_path = os.path.join(PROCESSORS_FOLDER, f"{processor_id}.yaml")

        if not os.path.exists(file_path):
            return {"message":f"Processor with id {processor_id} not found"}, 404
        

        # ------------------------------------------------------------------------------
        # delete the dag to the edge processor
        response = requests.delete(processor_urls["PROCESSOR_"+processor_id+"_URL"]+PROCESSOR_DELETE_SUFFIX)
        status_code = response.status_code
        if status_code not in [200, 202, 204]:
            logger.error(f"Delete DAG request for processor with id {processor_id} failed", response)
            return response.json(), status_code
        # ------------------------------------------------------------------------------


        # Replace the content of the YAML file with an empty YAML content
        with open(file_path, 'w') as file:
            file.write("")

        logger.info(f"DELETE request successful for processor with id {processor_id}")
        return jsonify({"message": f"Processor with id {processor_id} deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processor: {str(e)}")
        abort(500, "An error occurred while deleting the processor")


@app.route('/processors', methods=['DELETE'])
def delete_all_processors():
    logger.debug("DELETE request received for all processors")

    success_list = []
    try:
        # Iterate over all processor YAML files and replace their content with empty YAML content
        for processor_id in processor_ids:
            file_name = processor_id + ".yaml"
            file_path = os.path.join(PROCESSORS_FOLDER, file_name)
            if not os.path.exists(file_path):
                return {"message":f"Processor with id {processor_id} not found", "successfully_deleted" : success_list}, 404
        
            # ------------------------------------------------------------------------------
            # delete the dag to the edge processor
            response = requests.delete(processor_urls["PROCESSOR_"+processor_id+"_URL"]+PROCESSOR_DELETE_SUFFIX)
            status_code = response.status_code
            if status_code not in [200, 202, 204]:
                logger.debug(f"Delete DAG request for processor with id {processor_id} failed", response)
                return {"message" : json.dumps(response.json()), "successfully_deleted" : success_list}, status_code
            # ------------------------------------------------------------------------------

            with open(file_path, 'w') as file:
                file.write("")

            success_list.append(processor_id)

        logger.info("DELETE request successful for processors : ", success_list)
        return {"message": "All processors deleted successfully", "successfully_deleted" : success_list}, 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processors: {str(e)}")
        return {"message":"An error occurred while deleting the processors", "successfully_deleted" : success_list}, 500

if __name__ == '__main__':
    app.run(host=f"{HOST}", port=f"{PORT}", debug=True)

