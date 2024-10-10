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

from pydantic import BaseModel, ConfigDict
from typing import Optional

from workflow_orchestration.stage import StageParameters


class MapReduceSubsection(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    type: str
    subtype: str
    config: Optional[dict] = {}


class MapReduceParameters(BaseModel):
    model_config = ConfigDict(extra='forbid')
    map_function: MapReduceSubsection
    compute_function: MapReduceSubsection
    reduce_function: MapReduceSubsection


def create_dummy_compute_stage(compute_function_info):
    stg = {
        "name": compute_function_info.name,
        "type": compute_function_info.type,
        "subtype": compute_function_info.subtype,
        "config": compute_function_info.config,
    }

    stage = StageParameters(stg)
    return stage
