import logging
import yaml
import json
import requests

from processors import *

logger = logging.getLogger(__name__)

def parse_alert(alert_json):
    rule_id = alert_json['labels']['alertname']
    processor_id = alert_json['labels']['processor']
    status = alert_json['status']
    return rule_id, processor_id, status

def handle_delete_dag(processor_id):
    _, status_code = delete_processor_config(processor_id)
    if status_code not in [200, 202, 204]:
        logger.error(f"Could not delete the processor with id {processor_id}, response is {response.json()}, {status_code}")

def handle_create_dag(processor_id, action_json, manager_url):
    processor = {}
    processor["processors"] = action_json["processors"]
    processor["dag"] = action_json["dag"]
    processor_yaml = yaml.dump(processor)

    response = requests.post(f"{manager_url}/api/v1/processor_config/{processor_id}", processor_yaml)
    status_code = response.status_code
    if status_code not in [200, 201]:
        logger.error(f"Could not create the processor with id {processor_id}, response is {response.json()}, {status_code}")

    
