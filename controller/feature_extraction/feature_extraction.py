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
from common.configuration_api import TYPE_EXTRACT, SUBTYPE_EXTRACT_TSFEL, SUBTYPE_EXTRACT_TSFRESH


logger = logging.getLogger(__name__)
def feature_extraction(subtype, config, signals_list):
    # switch based on the configuration feature_extraction type
    if subtype == SUBTYPE_EXTRACT_TSFEL:
        logger.info("using tsfel feature_extraction")
        from feature_extraction.feature_extraction_tsfel import extract
        extracted_signals = extract(signals_list)
    elif subtype == SUBTYPE_EXTRACT_TSFRESH:
        logger.info("using tsfresh feature_extraction")
        from feature_extraction.feature_extraction_tsfresh import extract
        extracted_signals = extract(signals_list)
    else:
        raise "unsupported feature_extraction configuration"
    return extracted_signals
