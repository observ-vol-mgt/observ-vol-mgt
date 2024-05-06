from config import *
from instance import *
from flask import Flask, jsonify, request, Blueprint
import requests
import logging
import os
import yaml
import json

from utils.file_ops.processors import *
from utils.communication.processors import *
from models.ProcessorsConfig import ProcessorsConfig
from pydantic import ValidationError

processor_bp = Blueprint('processor', __name__)
processor_bp.config.from_pyfile('instance/config.yml')

# Filter variables from config.py that match the pattern 'PROCESSOR_*_URL' to get the URLs for the edge processors
processor_urls = {key: value for key, value in globals().items() if key.endswith('_URL') and key.startswith('PROCESSOR_')}

logger = logging.getLogger(__name__)

os.makedirs(PROCESSORS_FOLDER, exist_ok=True)
processor_ids = load_processors(processor_urls, PROCESSORS_FOLDER)


@processor_bp.route('/processors/<processor_id>', methods=['GET'])
def get_processor(processor_id):
    logger.debug(f"GET request received for processor with id {processor_id}")
    if processor_id not in processor_ids:
        return {"message":f"Processor with id {processor_id} not found"}, 404
    try:
        processor_data = read_processor_file(PROCESSORS_FOLDER, processor_id)
        logger.info(f"GET request successful for processor with id {processor_id}")
        return jsonify(processor_data), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        return {"message" : "An error occurred while processing the request"}, 500

@processor_bp.route('/processors', methods=['GET'])
def get_all_processors():
    try:
        processor_list = []
        for processor_id in processor_ids:
            processor_data = read_processor_file(PROCESSORS_FOLDER, processor_id)
            processor_list.append(processor_data)
        
        logger.error(processor_list)
        logger.info("GET request successful for all processors")
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


@processor_bp.route('/processors/<processor_id>', methods=['POST'])
def create_processor(processor_id):
    logger.debug(f"CREATE request received for processor with id {processor_id}")
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

        file_path = os.path.join(PROCESSORS_FOLDER, f"{processor_id}.yaml")
        if not os.path.exists(file_path):
            return {"message":f"Processor with id {processor_id} not found"}, 404
        if os.path.getsize(file_path) > 0:
            logger.warning(f"File with id {processor_id} already had some content. It will be replaced.")

        response = add_processor(processor_urls["PROCESSOR_"+processor_id+"_URL"], processor_data_yaml)
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


@processor_bp.route('/processors', methods=['POST'])
def create_all_processors():
    logger.debug("CREATE request received for all processors")
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

            response = add_processor(processor_urls["PROCESSOR_"+processor_id+"_URL"], processor_data_yaml)
            status_code = response.status_code
            if status_code not in [200, 201]:
                logger.error(f"Create DAG request for processor with id {processor_id} failed with the following response: {response}")
                return {"message" : json.dumps(response.json()), "successfully_created": success_list}, status_code
            
            create_or_replace_processor_file(PROCESSORS_FOLDER, processor_id, processor_data)
            success_list.append(processor_id)

        logger.info(f"POST request successful for processors : {success_list}")
        return jsonify({"message": "Create All request completed", "successfully_created": success_list}), 201

    except Exception as e:
        logger.error(f"Error occurred while creating all processors: {str(e)}")
        return {"message" : "An error occurred while creating all processors", "successfully_created": success_list}, 500


@processor_bp.route('/processors/<processor_id>', methods=['DELETE'])
def delete_processor(processor_id):
    logger.debug(f"DELETE request received for processor with id {processor_id}")
    try:
        if processor_id not in processor_ids:
            return {"message":f"Processor with id {processor_id} not found"}, 404
        
        response = remove_processor(processor_urls["PROCESSOR_"+processor_id+"_URL"])
        status_code = response.status_code
        if status_code not in [200, 202, 204]:
            logger.error(f"Delete DAG request for processor with id {processor_id} failed with the following response {response}")
            return response.json(), status_code

        delete_processor_file(PROCESSORS_FOLDER, processor_id)

        logger.info(f"DELETE request successful for processor with id {processor_id}")
        return jsonify({"message": f"Processor with id {processor_id} deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processor: {str(e)}")
        return {"message" : "An error occurred while deleting the processor"}, 500


@processor_bp.route('/processors', methods=['DELETE'])
def delete_all_processors():
    logger.debug("DELETE request received for all processors")

    success_list = []
    try:
        for processor_id in processor_ids:
            _, status_code = delete_processor(processor_id)

            if status_code in [200, 202, 204]:
                success_list.append(processor_id)

        logger.info(f"DELETE request successful for processors : {success_list}")
        return {"message": "All processors deleted successfully", "successfully_deleted" : success_list}, 200

    except Exception as e:
        logger.error(f"Error occurred while deleting processors: {str(e)}")
        return {"message":"An error occurred while deleting the processors", "successfully_deleted" : success_list}, 500
