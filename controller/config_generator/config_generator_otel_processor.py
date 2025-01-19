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
from jinja2 import Environment, FileSystemLoader


import common.configuration_api as api
from config_generator.config_generator_common import generate_common, record_results

logger = logging.getLogger(__name__)


def generate(config, extracted_signals, signals_to_keep, signals_to_reduce):
    if len(config.metrics_frequency) > 0:
        if config.counter_default_interval == "":
            config.counter_default_interval = api.counter_default_interval_default
        template_file = 'config_generator/templates/processor_filter_otel_processor_extended_template.yaml'
    elif config.counter_default_interval != "":
        template_file = 'config_generator/templates/processor_filter_otel_processor_interval_template.yaml'
    else:
        template_file = 'config_generator/templates/processor_filter_otel_processor_template.yaml'

    context_per_processor = generate_common(config, extracted_signals, signals_to_keep, signals_to_reduce)

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)

    for processor_id, processor_context in context_per_processor.items():
        logger.info(f", processor_id = {processor_id}, processor_context = \n{processor_context}")
        output = template.render(processor_context, interval_value=config.counter_default_interval)
        logger.info(f"output = \n{output}")

        record_results(config, extracted_signals, output, processor_id)

    return
