import logging
import os
import re
from string import Template

import requests
from common.utils import add_slash_to_dir
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


def generate_common(config, extracted_signals, signals_to_keep, signals_to_reduce):
    context_per_processor_reduce = generate_reduce(config, extracted_signals, signals_to_reduce)
    context_per_processor_adjust = generate_adjust(config, extracted_signals, signals_to_keep)

    # writing and sending configuration to relevant processors based on configuration
    # combine the contexts
    context_per_processor = {}
    for processor_id, processor_context in context_per_processor_reduce.items():
        context_per_processor[processor_id] = processor_context
    for processor_id, processor_context in context_per_processor_adjust.items():
        if processor_id not in context_per_processor:
            context_per_processor[processor_id] = {}
        for key, value in processor_context.items():
            context_per_processor[processor_id][key] = value

    logger.info(f"context_per_processor = \n{context_per_processor}")
    return context_per_processor


def generate_reduce(config, extracted_signals, signals_to_reduce):
    signal_filter_template = config.signal_filter_reduce_template
    processor_id_template = config.processor_id_template
    signal_name_template = config.signal_name_template
    signal_condition_template = config.signal_condition_template

    # if signal filtering template is set, filter signals
    if signal_filter_template != "":
        signals_to_reduce = [signal_name for signal_name in signals_to_reduce if re.search(
            signal_filter_template, signal_name)]

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


def generate_adjust(config, extracted_signals, signals_to_keep):
    signal_filter_template = config.signal_filter_adjust_template
    processor_id_template = config.processor_id_template
    signal_name_template = config.signal_name_template
    signal_condition_template = config.signal_condition_template
    logger.debug(f"config = {config}")

    logger.info(f"metrics_adjustment = {config.metrics_adjustment}")

    # if signal filtering template is set, filter signals
    signals_to_adjust = signals_to_keep
    if signal_filter_template != "":
        signals_to_adjust = [signal_name for signal_name in signals_to_adjust if re.search(
            signal_filter_template, signal_name)]

    logger.debug(f" ********* signals_to_adjust = {signals_to_adjust}")
    context_per_processor = {}

    # building context per each of the processors with signals to adjust (for the jinja template)
    for _id, signal_name in enumerate(signals_to_adjust):
        signal = extracted_signals.filter_by_names(signal_name)[0]
        signal_name = Template(signal_name_template).safe_substitute(signal.metadata)
        match = False
        for item in config.metrics_adjustment:
            if re.search(item.name_template, signal_name):
                if len(item.tag_filter) > 0:
                    if signal.is_tagged(item.tag_filter, True):
                        match = True
                        interval = item.interval
                        break
                else:
                    match = True
                    interval = item.interval
                    break

        if not match:
            continue

        signal_to_adjust = {"id": _id,
                            "name": signal_name,
                            "interval": interval,
                            "condition": Template(signal_condition_template).safe_substitute(signal.metadata)
                            }
        processor_id = Template(processor_id_template).safe_substitute(signal.metadata)

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


def record_result_per_processor(config, extracted_signals, output, processor_id):
    directory = config.directory
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


def record_results(config, context_per_processor, extracted_signals, template_file):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    for processor_id, processor_context in context_per_processor.items():
        logger.info(f", processor_id = {processor_id}, processor_context = \n{processor_context}")
        output = template.render(processor_context, config=config)
        logger.info(f"output = \n{output}")
        record_result_per_processor(config, extracted_signals, output, processor_id)
