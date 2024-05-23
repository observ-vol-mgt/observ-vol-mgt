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
    PIPELINE_INGEST_DUMMY = "dummy"
    PIPELINE_INGEST_FILE = "file"
    PIPELINE_INGEST_PROMQL = "promql"

class ExtractSubType(Enum):
    PIPELINE_EXTRACT_TSFEL = "tsfel"
    PIPELINE_EXTRACT_TSFRESH = "tsfresh"

class GeneratorSubType(Enum):
    PIPELINE_GENERATOR_NONE = "none"
    PIPELINE_GENERATOR_OTEL = "otel"
    PIPELINE_GENERATOR_PROCESSOR = "processor"

class GenerateInsightsType(Enum):
    INSIGHTS_SIMILARITY_METHOD_PEARSON = "pearson"
    INSIGHTS_SIMILARITY_METHOD_SPEARMAN = "spearman"
    INSIGHTS_SIMILARITY_METHOD_KENDALL = "kendall"

class IngestFile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    file_name: str
    filter_metadata: Optional[str] = ""
    ingest_name_template: Optional[str] = ""

class IngestPromql(BaseModel):
    model_config = ConfigDict(extra='forbid')
    url: str
    ingest_window: str # should be a time interval

class IngestDummy(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ExtractTsfel(BaseModel):
    model_config = ConfigDict(extra='forbid')

class ExtractTsfresh(BaseModel):
    model_config = ConfigDict(extra='forbid')

class GenerateInsights(BaseModel):
    model_config = ConfigDict(extra='forbid')
    pairwise_similarity_threshold: Optional[float] = 0.95
    compound_similarity_threshold: Optional[float] = 0.99
    compound_similarity_method: Optional[str] = GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_PEARSON.value

class GeneratorOtel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    directory: Optional[str] = "/tmp"

class GeneratorProcessor(BaseModel):
    model_config = ConfigDict(extra='forbid')


class GeneratorNone(BaseModel):
    model_config = ConfigDict(extra='forbid')

