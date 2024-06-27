from config import *
from flask import Flask, jsonify, request, Blueprint
import logging
import requests
import os
import yaml

controller_bp = Blueprint('controller', __name__)
logger = logging.getLogger(__name__)

controller_bp.config = {}

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    controller_bp.config.update(load_config(config_file))

CONTROLLER_URL = controller_bp.config['CONTROLLER_URL']

@controller_bp.route('/analyze', methods=['POST'])
def trigger_analyze():
    """
    Triggers the analysis process by calling the controller.
    ---
    tags:
      - Controller
    responses:
      201:
        description: Successfully triggered controller to run analysis
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Response data from the controller
      500:
        description: Error occurred while calling controller
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message
    """
    logger.debug("Analyze request submitted, calling the controller...")
    try:
        response = requests.post(CONTROLLER_URL)
        status_code = response.status_code
        if status_code not in [200, 201]:
            logger.error(f"Controller was not able to run the analysis pipeline", response)
            return response.json(), status_code
        return {"message":"success"}, 201
    except Exception as e:
        logger.error(f"Error occurred while calling controller: {str(e)}")
        return {"message" : f"An error occurred while calling controller: {str(e)}"}, 500
