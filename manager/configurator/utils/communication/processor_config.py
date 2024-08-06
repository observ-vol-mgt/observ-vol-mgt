import yaml
import requests
import json
import logging

logger = logging.getLogger(__name__)


def add_processor_config(processor_url, processor_json):
    processor_yaml = yaml.dump(processor_json)
    response = requests.post(processor_url+"/create", processor_yaml)
    return response


def remove_processor_config(processor_url):
    empty_data = {}
    response = requests.post(processor_url+"/delete")
    return response

