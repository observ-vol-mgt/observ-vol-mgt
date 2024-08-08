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
import common.configuration_api as api

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
    elif subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_OTEL.value:
        typed_config = api.ConfigGeneratorOtel(**config)
        logger.debug("using otel config_generator")
        from config_generator.config_generator_otel import generate
        r_value = generate(typed_config, extracted_signals,
                           signals_to_keep, signals_to_reduce)
    elif subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_PROCESSOR.value:
        typed_config = api.ConfigGeneratorProcessor(**config)
        logger.debug("using processor config_generator")
        from config_generator.config_generator_processor import generate
        r_value = generate(typed_config, extracted_signals,
                           signals_to_keep, signals_to_reduce)
    elif subtype == api.ConfigGeneratorSubType.PIPELINE_CONFIG_GENERATOR_OTEL_PROCESSOR.value:
        typed_config = api.ConfigGeneratorOtelProcessor(**config)
        logger.debug("using oTel processor config_generator")
        from config_generator.config_generator_otel_processor import generate
        r_value = generate(typed_config, extracted_signals,
                           signals_to_keep, signals_to_reduce)
    else:
        raise "unsupported feature_extraction configuration"
    return [r_value]
