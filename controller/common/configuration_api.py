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

from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

class StageType(Enum):
    INGEST = 1
    EXTRACT = 2
    INSIGHTS = 3
    CONFIG_GEN = 4

class IngestSubType(Enum):
    DUMMY = 1
    FILE = 2
    PROMQL = 3

class ExtractSubType(Enum):
    TSFEL = 1
    TSFRESH = 2

class ConfigIngestFile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    file_name: str
    filter_metadata: Optional[str] = ""

class ConfigIngestPromql(BaseModel):
    model_config = ConfigDict(extra='forbid')
    url: str
    ingest_window: str # should be a time interval

class ConfigIngestDummy(BaseModel):
    model_config = ConfigDict(extra='forbid')


TYPE_INGEST = 'ingest'
TYPE_EXTRACT = 'extract'
TYPE_INSIGHTS = 'insights'
TYPE_CONFIG_GENERATOR = 'config_generator'

SUBTYPE_INGEST_FILE = 'file'
SUBTYPE_INGEST_DUMMY = 'dummy'
SUBTYPE_INGEST_PROMQL = 'promql'

SUBTYPE_EXTRACT_TSFEL = 'tsfel'
SUBTYPE_EXTRACT_TSFRESH = 'tsfresh'

SUBTYPE_CONFIG_GENERATOR_NONE = 'none'
SUBTYPE_CONFIG_GENERATOR_OTEL = 'otel'
SUBTYPE_CONFIG_GENERATOR_PROCESSOR = 'processor'

