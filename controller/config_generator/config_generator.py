import logging
from common.conf import get_configuration

logger = logging.getLogger(__name__)


def config_generator(extracted_signals, signals_to_keep, signals_to_reduce):
    # switch based on the configuration config_generator type
    if get_configuration().config_generator_type == "none":
        logger.info("not generating configuration")
        r_value = "not generating configuration"
    elif get_configuration().config_generator_type == "otel":
        logger.info("using otel config_generator")
        from config_generator.config_generator_otel import generate
        r_value = generate(extracted_signals, signals_to_keep, signals_to_reduce)
    elif get_configuration().config_generator_type == "processor":
        logger.info("using processor config_generator")
        from config_generator.config_generator_processor import generate
        r_value = generate(extracted_signals, signals_to_keep, signals_to_reduce)
    else:
        raise "unsupported feature_extraction configuration"
    return r_value
