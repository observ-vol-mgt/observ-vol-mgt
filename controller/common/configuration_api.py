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
from typing import Optional, Union

class StageType(Enum):
    INGEST = "ingest"
    EXTRACT = "extract"
    INSIGHTS = "insights"
    CONF_GEN = "config_generator"

class IngestSubType(Enum):
    INGEST_DUMMY = "dummy"
    INGEST_FILE = "file"
    INGEST_PROMQL = "promql"

class ExtractSubType(Enum):
    EXTRACT_TSFEL = "tsfel"
    EXTRACT_TSFRESH = "tsfresh"

class ConfigGenSubType(Enum):
    CONF_GENERATOR_NONE = 'none'
    CONF_GENERATOR_OTEL = 'otel'
    CONF_GENERATOR_PROCESSOR = 'processor'

class ConfigIngestFile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    file_name: str
    filter_metadata: Optional[str] = ""
    ingest_name_template: Optional[str] = ""

class ConfigIngestPromql(BaseModel):
    model_config = ConfigDict(extra='forbid')
    url: str
    ingest_window: str # should be a time interval

class ConfigIngestDummy(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ConfigExtractTsfel(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ConfigExtractTsfresh(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ConfigGenerateInsights(BaseModel):
    model_config = ConfigDict(extra='forbid')
    pairwise_similarity_threshold: Optional[float] = 0.95
    compound_similarity_threshold: Optional[float] = 0.99
    compound_similarity_method: Optional[str] = 'pearson' # change to Enum?

class ConfigConfGenOtel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    directory: Optional[str] = "/tmp"

class ConfigConfGenProcessor(BaseModel):
    model_config = ConfigDict(extra='forbid')


class ConfigConfGenNone(BaseModel):
    model_config = ConfigDict(extra='forbid')

