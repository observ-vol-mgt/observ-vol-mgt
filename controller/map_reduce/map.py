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


def _map(subtype, config, input_data):
    logger.debug(f"inside map function, subtype = {subtype}")
    logger.debug(f"map config = {config}")
    logger.debug(f"len(input_data) = {len(input_data)}")
    if len(input_data) != 1:
        raise "extract configuration should have one input"

    signals = input_data[0]
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.MapSubType.PIPELINE_MAP_SIMPLE.value:
        logger.debug("using simple mapper")
        typed_config = api.MapSimple(**config)
        from map_reduce.simple_map import _map
        output_lists = _map(typed_config, signals)
    elif subtype == api.MapSubType.PIPELINE_MAP_BY_NAME.value:
        logger.debug("using map by name")
        typed_config = api.MapByName(**config)
        from map_reduce.by_name_clustering import _map
        output_lists = _map(typed_config, signals)
    else:
        raise "unsupported map configuration"
    logger.debug(f"**************************** after map, subtype = {subtype}")
    logger.debug(f"**************************** len(output_lists) = {len(output_lists)}")
    return output_lists
