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
    METADATA_EXTRACTION = "extract"
    INSIGHTS = "insights"
    CONFIG_GENERATOR = "config_generator"
    METADATA_CLASSIFICATION = "metadata_classification"
    MAP_REDUCE = "map_reduce"


class MetadataClassificationSubType(Enum):
    PIPELINE_METADATA_CLASSIFICATION_ZERO_SHOT = "metadata_classification_zero_shot"


class MetadataClassificationZeroShot(BaseModel):
    model_config = ConfigDict(extra='forbid')
    model: Optional[str] = "roberta-large-mnli"
    zero_shot_classification_file: Optional[str] = ("./metadata_classification/data"
                                                    "/observability_metrics_classification_zero_shot.json")


class IngestSubType(Enum):
    PIPELINE_INGEST_DUMMY = "dummy"
    PIPELINE_INGEST_FILE = "file"
    PIPELINE_INGEST_PROMQL = "promql"


class ExtractSubType(Enum):
    PIPELINE_EXTRACT_TSFEL = "tsfel"
    PIPELINE_EXTRACT_TSFRESH = "tsfresh"


class ConfigGeneratorSubType(Enum):
    PIPELINE_CONFIG_GENERATOR_NONE = "none"
    PIPELINE_CONFIG_GENERATOR_OTEL = "otel"
    PIPELINE_CONFIG_GENERATOR_PROCESSOR = "processor"


class GenerateInsightsType(Enum):
    INSIGHTS_SIMILARITY_METHOD_PEARSON = "pearson"
    INSIGHTS_SIMILARITY_METHOD_SPEARMAN = "spearman"
    INSIGHTS_SIMILARITY_METHOD_KENDALL = "kendall"

class MapSubType(Enum):
    PIPELINE_MAP_SIMPLE = "simple"
    PIPELINE_MAP_BY_NAME = "by_name"

class ReduceSubType(Enum):
    PIPELINE_REDUCE_SIMPLE = "simple"


class IngestFile(BaseModel):
    model_config = ConfigDict(extra='forbid')
    file_name: str
    filter_metadata: Optional[str] = ""
    ingest_name_template: Optional[str] = ""


class IngestPromql(BaseModel):
    model_config = ConfigDict(extra='forbid')
    url: str
    ingest_window: str  # should be a time interval
    filter_metadata: Optional[str] = ""
    ingest_name_template: Optional[str] = ""


class IngestDummy(BaseModel):
    model_config = ConfigDict(extra='forbid')


class FeatureExtractionTsfel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    features_json_file:  Optional[str] = "feature_extraction/tsfel_conf/limited_statistical.json"
    resample_rate: Optional[str] = "30s"
    sampling_frequency: Optional[float] = (1/30)


class FeatureExtractionTsfresh(BaseModel):
    model_config = ConfigDict(extra='forbid')


class GenerateInsights(BaseModel):
    model_config = ConfigDict(extra='forbid')
    pairwise_similarity_threshold: Optional[float] = 0.95
    pairwise_similarity_method: Optional[str] = GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_PEARSON.value
    compound_similarity_threshold: Optional[float] = 0.99


class ConfigGeneratorOtel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    directory: Optional[str] = "/tmp"


class ConfigGeneratorProcessor(BaseModel):
    model_config = ConfigDict(extra='forbid')
    # Template to extract the processor id from the signal metadata
    processor_id_template: Optional[str] = ""
    # Template to extract the metric name from the signal metadata
    signal_name_template: Optional[str] = ""
    signal_condition_template: Optional[str] = ""
    # Template to filter just a subset of the signals to be dropped by the processor
    signal_filter_template: Optional[str] = ""
    directory: Optional[str] = None
    url: Optional[str] = None


class GeneratorNone(BaseModel):
    model_config = ConfigDict(extra='forbid')

class MapSimple(BaseModel):
    model_config = ConfigDict(extra='forbid')
    number: int

class MapByName(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name_pattern: str

class ReduceSimple(BaseModel):
    model_config = ConfigDict(extra='forbid')
