from flask import Flask, jsonify, request, Blueprint
import requests
import logging
import os
import yaml
import json

from utils.file_ops.processor_config import *
from utils.communication.processor_config import *
from models.ProcessorsConfig import ProcessorsConfig
from pydantic import ValidationError

processor_bp = Blueprint('processor', __name__)
processor_bp.config = {}

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    processor_bp.config.update(load_config(config_file))

# Filter variables from config.py that match the pattern 'PROCESSOR_*_URL' to get the URLs for the edge processors
processor_urls = {key: value for key, value in processor_bp.config.items() if key.endswith('_URL') and key.startswith('PROCESSOR_')}

logger = logging.getLogger(__name__)

PROCESSORS_FOLDER=processor_bp.config['PROCESSORS_FOLDER']

os.makedirs(PROCESSORS_FOLDER, exist_ok=True)
processor_ids = load_processors(processor_urls, PROCESSORS_FOLDER)


@processor_bp.route('/processor_config/<processor_id>', methods=['GET'])
def get_processor_config(processor_id):
    logger.debug(f"GET config request received for processor with id {processor_id}")
    if processor_id not in processor_ids:
        return {"message":f"Processor with id {processor_id} not found"}, 404
    try:
        processor_data = read_processor_file(PROCESSORS_FOLDER, processor_id)
        logger.info(f"GET config request successful for processor with id {processor_id}")
        return jsonify(processor_data), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        return {"message" : "An error occurred while processing the request"}, 500

@processor_bp.route('/processor_config/', methods=['GET'])
def get_all_processors_config():
    try:
        processor_list = []
        for processor_id in processor_ids:
            processor_data = read_processor_file(PROCESSORS_FOLDER, processor_id)
            processor_list.append(processor_data)
        
        logger.error(processor_list)
        logger.info("GET config request successful for all processors")
        return jsonify(processor_list), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        return {"message" : "An error occurred while processing the request"}, 500


def validate_yaml(processor_data_yaml):
    if "processors" not in processor_data_yaml:
        raise Exception("processors field must be specified")
    processor_data_yaml_validated = ""
    if "dag" in processor_data_yaml:
        processor_data_yaml_validated = ProcessorsConfig(processors=processor_data_yaml["processors"], dag=processor_data_yaml["dag"])
    else:
        processor_data_yaml_validated = ProcessorsConfig(processors=processor_data_yaml["processors"])
    return processor_data_yaml_validated


@processor_bp.route('/processor_config/<processor_id>', methods=['POST'])
def update_processor_config(processor_id):
    logger.debug(f"POST config request received for processor with id {processor_id}")
    try:
        processor_data = request.get_data(as_text=True)

        # Validate if the provided data is valid YAML
        try:
            processor_data_yaml = yaml.safe_load(processor_data)
            processor_data_yaml_validated = validate_yaml(processor_data_yaml)
        except ValidationError as e:
            return jsonify({"message" : "Invalid YAML data", "error": e.errors()}), 400
        except Exception as e:
            return jsonify({"message" : "Error validating YAML data", "error": str(e)}), 500

        if processor_id not in processor_ids:
            return {"message":f"Processor with id {processor_id} not found"}, 404

        file_path = os.path.join(PROCESSORS_FOLDER, f"{processor_id}.yaml")
        if os.path.getsize(file_path) > 0:
            logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

        response = add_processor_config(processor_urls["PROCESSOR_"+processor_id+"_URL"], processor_data_yaml)
        status_code = response.status_code
        if status_code not in [200, 201]:
            logger.error(f"Create DAG request for processor with id {processor_id} failed", response)
            return response.json(), status_code

        create_or_replace_processor_file(PROCESSORS_FOLDER, processor_id, processor_data)

        logger.info(f"POST request successful for processor with id {processor_id}")
        return jsonify({"message":"success", "processor_id": processor_id}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating processor: {str(e)}")
        return {"message" : "An error occurred while creating the processor"}, 500


@processor_bp.route('/processor_config', methods=['POST'])
def update_all_processors_config():
    logger.debug("POST config request received for all processors")
    success_list = []
    try:
        processor_data = request.get_data(as_text=True)

        # Validate if the provided data is valid YAML
        try:
            processor_data_yaml = yaml.safe_load(processor_data)
            processor_data_yaml_validated = validate_yaml(processor_data_yaml)
        except ValidationError as e:
            return jsonify({"message" : "Invalid YAML data", "error": e.errors()}), 400
        except Exception as e:
            return jsonify({"message" : "Error validating YAML data", "error": str(e)}), 500

        for processor_id in processor_ids:
            file_name = processor_id + ".yaml"
            file_path = os.path.join(PROCESSORS_FOLDER, file_name)

            if not os.path.exists(file_path):
                return {"message":f"Processor with id {processor_id} not found", "successfully_created": success_list}, 404
            if os.path.getsize(file_path) > 0:
                logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

            response = add_processor_config(processor_urls["PROCESSOR_"+processor_id+"_URL"], processor_data_yaml)
            status_code = response.status_code
            if status_code not in [200, 201]:
                logger.error(f"Create DAG request for processor with id {processor_id} failed with the following response: {response}")
                return {"message" : json.dumps(response.json()), "successfully_created": success_list}, status_code
            
            create_or_replace_processor_file(PROCESSORS_FOLDER, processor_id, processor_data)
            success_list.append(processor_id)

        logger.info(f"POST config request successful for processors : {success_list}")
        return jsonify({"message": "POST All config request completed", "successfully_created": success_list}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating all processors: {str(e)}")
        return {"message" : "An error occurred while creating all processors", "successfully_created": success_list}, 500


@processor_bp.route('/processor_config/<processor_id>', methods=['DELETE'])
def delete_processor_config(processor_id):
    logger.debug(f"DELETE config request received for processor with id {processor_id}")
    try:
        if processor_id not in processor_ids:
            return {"message":f"Processor with id {processor_id} not found"}, 404
        
        response = remove_processor_config(processor_urls["PROCESSOR_"+processor_id+"_URL"])
        status_code = response.status_code
        if status_code not in [200, 202, 204]:
            logger.error(f"Delete DAG request for processor with id {processor_id} failed with the following response {response}")
            return response.json(), status_code

        delete_processor_file(PROCESSORS_FOLDER, processor_id)

        logger.info(f"DELETE config request successful for processor with id {processor_id}")
        return jsonify({"message": f"Processor with id {processor_id} deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processor: {str(e)}")
        return {"message" : "An error occurred while deleting the processor"}, 500


@processor_bp.route('/processor_config', methods=['DELETE'])
def delete_all_processors_config():
    logger.debug("DELETE config request received for all processors")

    success_list = []
    try:
        for processor_id in processor_ids:
            _, status_code = delete_processor(processor_id)

            if status_code in [200, 202, 204]:
                success_list.append(processor_id)

        logger.info(f"DELETE config request successful for processors : {success_list}")
        return {"message": "Processors config delete request completed", "successfully_deleted" : success_list}, 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processors: {str(e)}")
        return {"message":"An error occurred while deleting the processors", "successfully_deleted" : success_list}, 500
