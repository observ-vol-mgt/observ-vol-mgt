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
from string import Template

import requests
from jinja2 import Environment, FileSystemLoader
from common.utils import add_slash_to_dir
import re

logger = logging.getLogger(__name__)


def generate(config, extracted_signals, signals_to_keep, signals_to_reduce):
    directory = config.directory
    processor_id_template = config.processor_id_template
    signal_name_template = config.signal_name_template
    signal_condition_template = config.signal_condition_template

    logger.debug(f"generating processor configuration using: ")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('config_generator/templates/processor_filter_processor_template.yaml')
    context_per_processor = {}

    # building context per each of the processors with signals to drop (for the jinja template)
    for _id, signal_name in enumerate(signals_to_reduce):
        signal = extracted_signals.filter_by_names(signal_name)[0]
        signal_to_drop = {"id": _id,
                          "name": Template(signal_name_template).safe_substitute(signal.metadata),
                          "condition": Template(signal_condition_template).safe_substitute(signal.metadata)
                          }
        processor_id = Template(processor_id_template).safe_substitute(signal.metadata)

        if processor_id not in context_per_processor:
            context_per_processor[processor_id] = {"signals_to_drop": []}
        context_per_processor[processor_id]['signals_to_drop'].append(signal_to_drop)

    # writing and sending configuration to relevant processors based on configuration
    for processor_id, processor_context in context_per_processor.items():
        output = template.render(processor_context)

        # Write to file if directory exists in configuration
        if directory:
            response = write_to_file(directory+f"/{processor_id}", extracted_signals, output)
            logger.debug(f"write_to_file returned: {response}")

        # Send to processor URL if url exists in configuration
        url = config.url
        if url:
            response = send_to_processor(url, output, processor_id)
            logger.debug(f"send_to_processor returned: {response}")

    return


def send_to_processor(url, processor_configuration, processor_id):
    logger.debug(f"sending processor configuration to processor {processor_id} "
                 f" using: {url}")
    response = requests.post(f"{url}/api/v1/processors/{processor_id}", processor_configuration)
    logger.debug(f"response from processor: {response}")
    if response.status_code != 200:
        logger.error(f"Error sending configuration to processor: {url} response is: {response}")

    return response.status_code


def write_to_file(directory, extracted_signals, processor_configuration):
    logger.debug(f"writing processor configuration to file"
                 f" using: {directory}")

    output_dir = add_slash_to_dir(directory)
    source = re.sub('-+', '-', extracted_signals.metadata["ingest_source"].translate(str.maketrans("_/.", "---")))
    path = re.sub('/+', '/', f"{output_dir}/{source}")

    if not os.path.exists(path):
        os.makedirs(path)

    file_name = f"{path}/processor_filter_processor_config.yaml"
    with open(file_name, 'w') as f:
        f.write(processor_configuration)

    return f"Configuration file was written in processor format to {file_name}"
