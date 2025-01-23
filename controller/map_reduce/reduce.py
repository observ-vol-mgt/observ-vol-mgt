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


def reduce(subtype, config, input_data):
    logger.debug(f"inside reduce function, subtype = {subtype}")
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.ReduceSubType.PIPELINE_REDUCE_SIMPLE.value:
        logger.debug("using simple reduce")
        typed_config = api.ReduceSimple(**config)
        from map_reduce.simple_reduce import reduce
        output_list = reduce(typed_config, input_data)
    else:
        raise "unsupported reduce configuration"
    return output_list
