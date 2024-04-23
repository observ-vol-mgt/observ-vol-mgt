import yaml
import requests
import json
import logging

logger = logging.getLogger(__name__)

def add_processor(processor_url, processor_json):
    processor_yaml = yaml.dump(processor_json)
    response = requests.post(processor_url, processor_yaml)
    return response

def remove_processor(processor_url):
    empty_data = {}
    response = requests.post(processor_url, yaml.dump(empty_data))
    return response

