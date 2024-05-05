import logging
from jinja2 import Environment, FileSystemLoader

from common.conf import get_configuration
from common.utils import add_slash_to_dir

logger = logging.getLogger(__name__)


def generate(signals_to_keep, signals_to_reduce):
    logger.debug(f"generating otel configuration using: {signals_to_keep} {signals_to_reduce}")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('config_generator/templates/otel_filter_processor_template.yaml')
    context = {
        'metrics': []
    }
    for signal in signals_to_keep:
        context['metrics'].append({'name': signal, 'action': 'include'})

    output = template.render(context)
    output_dir = add_slash_to_dir(get_configuration().config_generator_directory)
    file_name = f"{output_dir}/otel_filter_processor_config.yaml"

    # Write the configuration to a file
    with open(file_name, 'w') as f:
        f.write(output)

    return f"Configuration file was written in Otel format to {file_name}"
