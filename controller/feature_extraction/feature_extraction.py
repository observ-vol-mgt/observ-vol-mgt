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

logger = logging.getLogger(__name__)
def feature_extraction(extract_stage, signals_list):
    # switch based on the configuration feature_extraction type
    if extract_stage.subtype == "tsfel":
        logger.info("using tsfel feature_extraction")
        from feature_extraction.feature_extraction_tsfel import extract
        extracted_signals = extract(signals_list)
    elif extract_stage.subtype == "tsfresh":
        logger.info("using tsfresh feature_extraction")
        from feature_extraction.feature_extraction_tsfresh import extract
        extracted_signals = extract(signals_list)
    else:
        raise "unsupported feature_extraction configuration"
    return extracted_signals
