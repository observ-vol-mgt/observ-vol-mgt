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
