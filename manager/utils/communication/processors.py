import yaml
import requests
import json
import logging

logger = logging.getLogger(__name__)

def add_processor(processor_url, processor_yaml):
    return requests.post(processor_url, processor_yaml)

def delete_processor(processor_url):
    empty_data = {}
    response = requests.post(processor_url, yaml.dump(empty_data))
    return response

