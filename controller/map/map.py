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


def map(subtype, config, input_data):
    print("inside map function, subtype = ", subtype)
    if len(input_data) != 1:
        raise "feature_extraction configuration should have one input"
    signals_list = input_data[0]
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.MapSubType.PIPELINE_MAP_SIMPLE.value:
        logger.debug("using simple mapper")
        typed_config = api.MapSimple(**config)
        from map.simple_map import map
        output_lists = map(typed_config, signals_list)
    elif subtype == api.MapSubType.PIPELINE_MAP_BY_NAME.value:
        logger.debug("using map by name")
        typed_config = api.MapByName(**config)
        from map.by_name_clustering import map
        output_lists = map(typed_config, signals_list)
    else:
        raise "unsupported map configuration"
    return output_lists
