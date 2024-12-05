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
import re

from config_generator.config_generator import generate_reduce, generate_monotonic, send_to_processor, \
    write_to_file

logger = logging.getLogger(__name__)


def generate(config, extracted_signals, signals_to_keep, signals_to_reduce):
    context_per_processor_reduce = generate_reduce(config, extracted_signals, signals_to_keep, signals_to_reduce)
    context_per_processor_monotonic = generate_monotonic(config, extracted_signals, signals_to_keep, signals_to_reduce)
    # writing and sending configuration to relevant processors based on configuration

    # combine the contexts
    context_per_processor = {}
    for processor_id, processor_context in context_per_processor_reduce.items():
        context_per_processor[processor_id] = processor_context
    for processor_id, processor_context in context_per_processor_monotonic.items():
        if processor_id not in context_per_processor:
            context_per_processor[processor_id] = {}
        for key, value in processor_context.items():
            context_per_processor[processor_id][key] = value

    directory = config.directory
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(
        'config_generator/templates/processor_filter_otel_processor_template.yaml')

    for processor_id, processor_context in context_per_processor.items():
        logger.info(f", processor_id = {processor_id}, processor_context = {processor_context}")
        output = template.render(processor_context)
        logger.info(f"output = {output}")

        # Write to file if directory exists in configuration
        if directory:
            response = write_to_file(
                directory + f"/{processor_id}", extracted_signals, output)
            logger.debug(f"write_to_file returned: {response}")

        # Send to processor URL if url exists in configuration
        url = config.url
        if url:
            response = send_to_processor(url, output, processor_id)
            logger.debug(f"send_to_processor returned: {response}")

    return

