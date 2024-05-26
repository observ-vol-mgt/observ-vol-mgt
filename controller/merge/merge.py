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


def merge(subtype, config, input_data):
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.MergeSubType.PIPELINE_MERGE_SIMPLE.value:
        logger.debug("using simple merge")
        typed_config = api.MergeSimple(**config)
        from merge.simple_merge import merge
        output_list = merge(typed_config, input_data)
    else:
        raise "unsupported split configuration"
    return output_list
