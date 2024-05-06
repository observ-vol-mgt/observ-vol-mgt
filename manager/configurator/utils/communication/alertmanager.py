import yaml
import requests
import json
import logging

logger = logging.getLogger(__name__)

def add_rule(rule, alertmanager_url):
    rule_id = rule["rule_id"]
    rule_json = {}
    rule_json["processors"] = rule["processors"]
    rule_json["expr"] = rule["expr"]
    rule_json["duration"] = rule["duration"]
    rule_json["description"] = rule["description"]

    rule_yaml = yaml.dump(rule_json)

    response = requests.post(f"{alertmanager_url}/{rule_id}", rule_yaml)
    return response 

def delete_rule(rule_id, alertmanager_url):
    response = requests.delete(f"{alertmanager_url}/{rule_id}")
    return response

