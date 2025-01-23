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
import common.configuration_api as api

logger = logging.getLogger(__name__)


def extract(subtype, config, input_data):
    if len(input_data) != 1:
        raise "extract configuration should have one input"
    signals_list = input_data[0]
    # switch based on the configuration extract type
    # verify config parameters conform to structure
    if subtype == api.ExtractSubType.PIPELINE_EXTRACT_TSFEL.value:
        tsfel_config = api.FeatureExtractionTsfel(**config)
        logger.debug("using tsfel feature_extraction")
        from extract.feature_extraction_tsfel import extract
        extracted_signals = extract(tsfel_config, signals_list)
    elif subtype == api.ExtractSubType.PIPELINE_EXTRACT_TRIM.value:
        logger.debug("using trim_time_series")
        from extract.trim_time_series import extract
        extracted_signals = extract(None, signals_list)
    else:
        raise "unsupported extract configuration"
    return [extracted_signals]
