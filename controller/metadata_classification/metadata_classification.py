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


def metadata_classification(subtype, config, input_data):
    if len(input_data) != 1:
        raise "metadata_classification configuration should have one input"
    signals_list = input_data[0]
    # switch based on the configuration metadata_classification type
    # verify config parameters conform to structure
    if subtype == api.MetadataClassificationSubType.PIPELINE_METADATA_CLASSIFICATION_ZERO_SHOT.value:
        zero_shot_config = api.MetadataClassificationZeroShot(**config)
        logger.info("using zero-shot metadata_classification")
        from metadata_classification.metadata_classification_zero_shot import metadata_classification
        classified_signals = metadata_classification(zero_shot_config, signals_list)
    else:
        raise "unsupported metadata_classification configuration"
    return [classified_signals]
