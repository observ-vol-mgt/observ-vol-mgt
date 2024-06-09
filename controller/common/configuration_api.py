"""

## Controller configuration

This document describes the configuration of the volume management controller component.
The configuration is stored in a YAML file, typically `config.yaml`.
The configuration is read by the controller component when it starts.
The configuration is provided to the `controller` using the `-c` command line argument.

Typical example usage:

    `./controller -c config.yaml`

The configuration is organized into two areas.

1. Pipeline definition - this area describes the pipeline stages and the relationship between stages.
 It includes only high-level configuration that does not describe the functionality of the pipeline, just
 provides names to stages, and describes the order of execution.

> For each stage, there is a named section, describing the functional behavior and
 configuration of the stage.

2. Stage configuration - For each `named stage`, describes the functionality of the stage using `Type` and `subType`.
  Additional specific configuration parameters according to the functionality.

"""

#   Copyright 2024 IBM, Inc.
#  #
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  #
#       http://www.apache.org/licenses/LICENSE-2.0
#  #
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional


class StageType(Enum):
    """
    Stage `type` (stage functionality):
    Each `named stage configuration` includes one of the following `type` (string) options:
    """
    INGEST = "ingest"  # `ingest`: ingest data from various sources into the controller
    FEATURES_EXTRACTION = "extract"  # `extract`: performs feature extraction on the signals
    INSIGHTS = "insights"  # `insights`: generates insights (analytics)
    CONFIG_GENERATOR = "config_generator"  # `config_generator`: Generates and apply processor configurations
    METADATA_CLASSIFICATION = "metadata_classification"  # `metadata_classification`: Metadata classification
    MAP_REDUCE = "map_reduce"  # `map_reduce`: apply map reduce operations (for stages scalability)


class MetadataClassificationSubType(Enum):
    """
    Enumerates subtypes for metadata classification.
    """
    PIPELINE_METADATA_CLASSIFICATION_ZERO_SHOT = "metadata_classification_zero_shot"
    PIPELINE_METADATA_CLASSIFICATION_FEW_SHOT = "metadata_classification_few_shot"


class MetadataClassificationFewShot(BaseModel):
    """
    Configuration for few-shot metadata classification.
    """
    model_config: ConfigDict  # Configuration for the model
    model: Optional[str] = "sentence-transformers/paraphrase-mpnet-base-v2"  # Pre-trained model to use
    few_shot_classification_file: Optional[str] = (
        "./metadata_classification/data/observability_metrics_classification_zero_shot.json"
    )  # File containing few-shot classification external data


class MetadataClassificationZeroShot(BaseModel):
    """
    Configuration for zero-shot metadata classification.
    """
    model_config: ConfigDict  # Configuration for the model
    model: Optional[str] = "roberta-large-mnli"  # Pre-trained model to use
    zero_shot_classification_file: Optional[str] = (
        "./metadata_classification/data/observability_metrics_classification_zero_shot.json"
    )  # File containing zero-shot classification external data


class IngestSubType(Enum):
    """
    Enumerates different subtypes for ingestion.
    """
    PIPELINE_INGEST_DUMMY = "dummy"
    PIPELINE_INGEST_FILE = "file"
    PIPELINE_INGEST_PROMQL = "promql"


class ExtractSubType(Enum):
    """
    Enumerates different subtypes for metadata extraction.
    """
    PIPELINE_EXTRACT_TSFEL = "tsfel"
    PIPELINE_EXTRACT_TSFRESH = "tsfresh"


class ConfigGeneratorSubType(Enum):
    """
    Enumerates different subtypes for configuration generation.
    """
    PIPELINE_CONFIG_GENERATOR_NONE = "none"
    PIPELINE_CONFIG_GENERATOR_OTEL = "otel"
    PIPELINE_CONFIG_GENERATOR_PROCESSOR = "processor"


class GenerateInsightsType(Enum):
    """
    Enumerates different types of insights generation methods.
    """
    INSIGHTS_SIMILARITY_METHOD_PEARSON = "pearson"
    INSIGHTS_SIMILARITY_METHOD_SPEARMAN = "spearman"
    INSIGHTS_SIMILARITY_METHOD_KENDALL = "kendall"


class MapSubType(Enum):
    """
    Enumerates different subtypes for map operations.
    """
    PIPELINE_MAP_SIMPLE = "simple"
    PIPELINE_MAP_BY_NAME = "by_name"


class ReduceSubType(Enum):
    """
    Enumerates different subtypes for reduce operations.
    """
    PIPELINE_REDUCE_SIMPLE = "simple"


class IngestFile(BaseModel):
    """
    Configuration for file ingestion.
    """
    model_config: ConfigDict  # Configuration for the model
    file_name: str  # Name of the file to ingest
    filter_metadata: Optional[str] = ""  # Metadata filter
    ingest_name_template: Optional[str] = ""  # Template for ingest names


class IngestPromql(BaseModel):
    """
    Configuration for PromQL ingestion.
    """
    model_config: ConfigDict  # Configuration for the model
    url: str  # URL to fetch data from
    ingest_window: str  # Time interval for ingestion
    filter_metadata: Optional[str] = ""  # Metadata filter
    ingest_name_template: Optional[str] = ""  # Template for ingest names


class IngestDummy(BaseModel):
    """
    Configuration for dummy ingestion.
    """
    model_config: ConfigDict  # Configuration for the model


class FeatureExtractionTsfel(BaseModel):
    """
    Configuration for feature extraction using TSFEL.
    """
    model_config: ConfigDict  # Configuration for the model
    features_json_file: Optional[str] = "feature_extraction/tsfel_conf/limited_statistical.json"  # JSON file for features
    resample_rate: Optional[str] = "30s"  # Resampling rate
    sampling_frequency: Optional[float] = (1/30)  # Sampling frequency


class FeatureExtractionTsfresh(BaseModel):
    """
    Configuration for feature extraction using TSFRESH.
    """
    model_config: ConfigDict  # Configuration for the model


class GenerateInsights(BaseModel):
    """
    Configuration for generating insights.
    """
    model_config: ConfigDict  # Configuration for the model
    pairwise_similarity_threshold: Optional[float] = 0.95  # Threshold for pairwise similarity
    pairwise_similarity_method: Optional[str] = GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_PEARSON.value  # Method for pairwise similarity
    compound_similarity_threshold: Optional[float] = 0.99  # Threshold for compound similarity


class ConfigGeneratorOtel(BaseModel):
    """
    Configuration for OpenTelemetry (OTel) configuration generation.
    """
    model_config: ConfigDict  # Configuration for the model
    directory: Optional[str] = "/tmp"  # Directory to store configuration


class ConfigGeneratorProcessor(BaseModel):
    """
    Configuration for processor-based configuration generation.
    """
    model_config: ConfigDict  # Configuration for the model
    processor_id_template: Optional[str] = ""  # Template for processor ID
    signal_name_template: Optional[str] = ""  # Template for signal name
    signal_condition_template: Optional[str] = ""  # Template for signal condition
    signal_filter_template: Optional[str] = ""  # Template for signal filter
    directory: Optional[str] = None  # Directory to store configuration
    url: Optional[str] = None  # URL to fetch data from


class GeneratorNone(BaseModel):
    """
    Placeholder configuration for no specific generation task.
    """
    model_config: ConfigDict  # Configuration for the model


class MapSimple(BaseModel):
    """
    Configuration for simple map operations.
    """
    model_config: ConfigDict  # Configuration for the model
    number: int  # Number for mapping


class MapByName(BaseModel):
    """
    Configuration for map operations by name pattern.
    """
    model_config: ConfigDict  # Configuration for the model
    name_pattern: str  # Pattern for mapping by name


class ReduceSimple(BaseModel):
    """
    Configuration for simple reduce operations.
    """
    model_config: ConfigDict  # Configuration for the model
