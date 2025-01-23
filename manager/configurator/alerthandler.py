from flask import Flask, jsonify, request, Blueprint
import logging
import os
import yaml
import json
import sys

from utils.communication.alerthandler import *
from utils.file_ops.rules import *

alerthandler_bp = Blueprint('alerthandler', __name__)
logger = logging.getLogger(__name__)

alerthandler_bp.config = {}

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    alerthandler_bp.config.update(load_config(config_file))

RULES_FOLDER = alerthandler_bp.config['RULES_FOLDER']


@alerthandler_bp.route('/alerthandler', methods=['POST'])
def handler():
    logger.debug("Alertmanager rule triggered, handling it now")
    try:
        alert_data = request.json
        if "alerts" not in alert_data:
            logger.error(f"The alert does not have the alerts field: {alert_data}")
            return {"message" : "Invalid Alert Data"}, 400

        for alert in alert_data["alerts"]:
            rule_id, processor_id, status = parse_alert(alert)
            logger.info(f"Alert {status} against rule id: {rule_id} for processors: {processor_id}")

            #fetch the rule file to get the action that needs to be performed
            rule_json = read_rule_file(RULES_FOLDER, rule_id)
            #check if the processor_id for which the alert is raised is actually in the list of processor for which this rule has been configured by the use
            if processor_id not in rule_json['processors']:
                continue

            action = status + "_action"
            if action in rule_json:
                if rule_json[action]['action_type'] == "delete_dag":
                    handle_delete_dag(processor_id)
                elif rule_json[action]['action_type'] == "create_dag":
                    handle_create_dag(processor_id, rule_json[action], request.url_root)
        return {"message" : "Gone through all the alerts"}, 201
    except Exception as e:
        logger.error(f"Error occurred while creating rules: {str(e)}")
        return {"message" : "An error occurred while creating rules", "successfully_created": success_list}, 500

