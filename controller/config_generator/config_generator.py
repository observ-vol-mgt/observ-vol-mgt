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
import re
from string import Template

import common.configuration_api as api
import requests

from common.utils import add_slash_to_dir

logger = logging.getLogger(__name__)


def config_generator(subtype, config, input_data):
    if len(input_data) != 3:
        raise "config_generator configuration should have 3 inputs"
    extracted_signals = input_data[0]
    signals_to_keep = input_data[1]
    signals_to_reduce = input_data[2]
    # switch based on the configuration config_generator type
    # verify config parameters conform to structure
    if subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_NONE.value:
        api.GeneratorNone(**config)
        logger.debug("not generating configuration")
        r_value = "not generating configuration"
    elif subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_PROCESSOR.value:
        typed_config = api.ConfigGeneratorProcessor(**config)
        logger.debug("using processor config_generator")
        from config_generator.config_generator_processor import generate
        r_value = generate(typed_config, extracted_signals,
                           signals_to_keep, signals_to_reduce)
    elif subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_OTEL_PROCESSOR.value:
        typed_config = api.ConfigGeneratorProcessor(**config)
        logger.debug("using oTel processor config_generator")
        from config_generator.config_generator_otel_processor import generate
        r_value = generate(typed_config, extracted_signals,
                           signals_to_keep, signals_to_reduce)
    else:
        raise "unsupported feature_extraction configuration"
    return [r_value]


def generate_reduce(config, extracted_signals, signals_to_keep, signals_to_reduce):
    signal_filter_template = config.signal_filter_template
    processor_id_template = config.processor_id_template
    signal_name_template = config.signal_name_template
    signal_condition_template = config.signal_condition_template

    # if signal filtering template is set, filter signals
    if signal_filter_template != "":
        signals_to_reduce = [signal_name for signal_name in signals_to_reduce if re.search(
            signal_filter_template, signal_name)]

    logger.debug("generating processor configuration using: ")
    context_per_processor = {}

    # building context per each of the processors with signals to drop (for the jinja template)
    for _id, signal_name in enumerate(signals_to_reduce):
        signal = extracted_signals.filter_by_names(signal_name)[0]
        signal_to_drop = {"id": _id,
                          "name": Template(signal_name_template).safe_substitute(signal.metadata),
                          "condition": Template(signal_condition_template).safe_substitute(signal.metadata)
                          }
        processor_id = Template(
            processor_id_template).safe_substitute(signal.metadata)

        if processor_id not in context_per_processor:
            context_per_processor[processor_id] = {"signals_to_drop": []}

        # Adding the signal to the list of signals to drop, only if the signal is not already added to the list
        found = False
        for added_signal in context_per_processor[processor_id]['signals_to_drop']:
            if (added_signal['name'] == signal_to_drop['name'] and
                    added_signal['condition'] == signal_to_drop['condition']):
                found = True
                break
        if not found:
            context_per_processor[processor_id]['signals_to_drop'].append(
                signal_to_drop)
    return context_per_processor


def generate_monotonic(config, extracted_signals, signals_to_keep, signals_to_reduce):
    signal_filter_template = config.signal_filter_template
    processor_id_template = config.processor_id_template
    signal_name_template = config.signal_name_template
    signal_condition_template = config.signal_condition_template

    # if signal filtering template is set, filter signals
    signals_to_adjust = signals_to_keep
    if signal_filter_template != "":
        signals_to_adjust = [signal_name for signal_name in signals_to_adjust if re.search(
            signal_filter_template, signal_name)]

    logger.debug("generating processor configuration using: ")
    context_per_processor = {}

    # building context per each of the processors with signals to drop (for the jinja template)
    for _id, signal_name in enumerate(signals_to_adjust):
        signal = extracted_signals.filter_by_names(signal_name)[0]
        if "tags" not in signal.metadata.keys():
            continue
        if not signal.is_tagged([InsightsAnalysisChainType.INSIGHTS_ANALYSIS_MONOTONIC.value], True):
            continue
        signal_to_adjust = {"id": _id,
                            "name": Template(signal_name_template).safe_substitute(signal.metadata),
                            "interval": str(config.monotonic_freq_interval),
                            "condition": Template(signal_condition_template).safe_substitute(signal.metadata)
                            }
        processor_id = Template(
            processor_id_template).safe_substitute(signal.metadata)

        if processor_id not in context_per_processor:
            context_per_processor[processor_id] = {"signals_to_adjust": []}

        # Adding the signal to the list of signals to adjust, only if the signal is not already added to the list
        found = False
        for added_signal in context_per_processor[processor_id]['signals_to_adjust']:
            if (added_signal['name'] == signal_to_adjust['name'] and
                    added_signal['condition'] == signal_to_adjust['condition']):
                found = True
                break
        if not found:
            context_per_processor[processor_id]['signals_to_adjust'].append(
                signal_to_adjust)
    return context_per_processor


def send_to_processor(url, processor_configuration, processor_id):
    logger.debug(f"sending processor configuration to processor {processor_id} "
                 f" using: {url}")
    response = requests.post(
        f"{url}/api/v1/processor_config/{processor_id}", processor_configuration)
    logger.debug(f"response from processor: {response}")
    if response.status_code not in [200, 201]:
        logger.error(
            f"Error sending configuration to processor: {url} response is: {response}")

    return response.status_code


def write_to_file(directory, extracted_signals, processor_configuration):
    logger.debug(f"writing processor configuration to file"
                 f" using: {directory}")

    output_dir = add_slash_to_dir(directory)
    source = re.sub('-+', '-',
                    extracted_signals.metadata["ingest_source"].translate(str.maketrans("_/.", "---")))
    path = re.sub('/+', '/', f"{output_dir}/{source}")

    if not os.path.exists(path):
        os.makedirs(path)

    file_name = f"{path}/processor_filter_processor_config.yaml"
    with open(file_name, 'w') as f:
        f.write(processor_configuration)

    return f"Configuration file was written in processor format to {file_name}"
