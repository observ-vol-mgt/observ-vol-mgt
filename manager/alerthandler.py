from config import *
from flask import Flask, jsonify, request, Blueprint
import logging
import os
import yaml
import json


alerthandler_bp = Blueprint('alerthandler', __name__)
logger = logging.getLogger(__name__)


@alerthandler_bp.route('/handler', methods=['POST'])
def handler():
    logger.debug("Alertmanager rule triggered, handling it now")
    success_list = []
    try:
        alert_data = request.get_data(as_text=True)
        # Validate if the provided data is valid YAML
        
        logger.error(alert_data)
        logger.info("Post rules request successful for rules : ", success_list)
        return jsonify({"message": "Post rules request completed", "successfully_created": success_list}), 201
    except Exception as e:
        logger.error(f"Error occurred while creating rules: {str(e)}")
        return {"message" : "An error occurred while creating rules", "successfully_created": success_list}, 500

