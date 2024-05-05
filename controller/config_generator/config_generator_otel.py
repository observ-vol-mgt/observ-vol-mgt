import logging
import os
import re

from jinja2 import Environment, FileSystemLoader

from common.conf import get_configuration
from common.utils import add_slash_to_dir

logger = logging.getLogger(__name__)


def generate(extracted_signals, signals_to_keep, signals_to_reduce):
    logger.debug(f"generating otel configuration using: {signals_to_keep} {signals_to_reduce}")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('config_generator/templates/otel_filter_processor_template.yaml')
    context = {
        'metrics': []
    }
    for signal in signals_to_keep:
        context['metrics'].append({'name': signal, 'action': 'include'})

    source = re.sub('-+', '-', extracted_signals.metadata["ingest_source"].translate(str.maketrans("_/.", "---")))
    output = template.render(context)
    output_dir = add_slash_to_dir(get_configuration().config_generator_directory)
    path = re.sub('/+', '/', f"{output_dir}/{source}")

    if not os.path.exists(path):
        os.makedirs(path)

    file_name = f"{path}/otel_filter_processor_config.yaml"
    with open(file_name, 'w') as f:
        f.write(output)

    return f"Configuration file was written in Otel format to {file_name}"
