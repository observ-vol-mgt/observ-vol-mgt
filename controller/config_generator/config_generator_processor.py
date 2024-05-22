#  Copyright 2024 IBM, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import os

import requests
from jinja2 import Environment, FileSystemLoader
from common.utils import add_slash_to_dir
import re

logger = logging.getLogger(__name__)


class ProcessorRuleFiringAction:
    def __init__(self, action_type, processors, dag):
        self.action_type = action_type
        self.processors = processors
        self.dag = dag


class ProcessorRule:
    def __init__(self, _id, processors, expr, duration, description, firing_action, resolved_action):
        self.id = _id
        self.processors = processors
        self.expr = expr
        self.duration = duration
        self.description = description
        self.firing_action = firing_action
        self.resolved_action = resolved_action


def generate(config, extracted_signals, signals_to_keep, signals_to_reduce):
    logger.debug(f"generating processor configuration using: ")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('config_generator/templates/processor_filter_processor_template.yaml')
    context = {
        'processor_rules': []
    }

    for i, signal in enumerate(signals_to_reduce):
        processor_rule = ProcessorRule(_id=i,
                                       processors=[i],
                                       expr='""',
                                       duration="1s",
                                       description=f'"Rule to reduce signal: {signal}"',
                                       firing_action=ProcessorRuleFiringAction(
                                           action_type="create_dag",
                                           processors=f"- type: filter\n"
                                                      f"id: f1\n"
                                                      f"metrics:\n"
                                                      f"    metric_name: {signal}\n"
                                                      f"    action: include",
                                           dag=f"- node: f1\n"
                                               "children: []"),
                                       resolved_action=f"action_type: delete_dag")
        context['processor_rules'].append(processor_rule)

    output = template.render(context)

    # Write to file if directory exists in configuration
    directory = config.directory
    if directory:
        response = write_to_file(directory, extracted_signals, output)
        logger.debug(f"write_to_file returned: {response}")

    # Send to processor URL if url exists in configuration
    url = config.url
    if url:
        response = send_to_processor(url, output)
        logger.debug(f"send_to_processor returned: {response}")

    return


def send_to_processor(url, processor_rules_as_text):
    logger.debug(f"sending processor configuration to processor"
                 f" using: {url}")
    response = requests.post(url+"/api/v1/rules", processor_rules_as_text)
    logger.debug(f"response from processor: {response}")
    if response.status_code != 200:
        logger.error(f"Error sending configuration to processor: {url} response is: {response}")

    return response.status_code


def write_to_file(directory, extracted_signals, processor_rules_as_text):
    logger.debug(f"writing processor configuration to file"
                 f" using: {directory}")

    output_dir = add_slash_to_dir(directory)
    source = re.sub('-+', '-', extracted_signals.metadata["ingest_source"].translate(str.maketrans("_/.", "---")))
    path = re.sub('/+', '/', f"{output_dir}/{source}")

    if not os.path.exists(path):
        os.makedirs(path)

    file_name = f"{path}/processor_filter_processor_config.yaml"
    with open(file_name, 'w') as f:
        f.write(processor_rules_as_text)

    return f"Configuration file was written in processor format to {file_name}"
