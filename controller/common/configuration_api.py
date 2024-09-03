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

from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class StageType(Enum):
    """
    Stage `type` (stage functionality):
    Each `named stage configuration` includes one of the following `type` (string) options:
    """
    INGEST = "ingest"  # `ingest`: ingest data from various sources into the controller
    # `extract`: performs feature extraction on the signals
    EXTRACT = "extract"
    INSIGHTS = "insights"  # `insights`: generates insights (analytics)
    # `config_generator`: Generates and apply processor configurations
    CONFIG_GENERATOR = "config_generator"
    # `metadata_classification`: Metadata classification
    METADATA_CLASSIFICATION = "metadata_classification"
    # `map_reduce`: apply map reduce operations (for stages scalability)
    MAP_REDUCE = "map_reduce"
    ENCODE = "encode"  # `encode`: encode data


class MetadataClassificationSubType(Enum):
    """
    Enumerates subtypes for metadata classification.
    """
    # `metadata_classification_regex`: uses regex to perform metadata classification
    PIPELINE_METADATA_CLASSIFICATION_REGEX = "metadata_classification_regex"
    # `metadata_classification_zero_shot`: uses zero-shot (AI) technique to perform metadata classification
    PIPELINE_METADATA_CLASSIFICATION_ZERO_SHOT = "metadata_classification_zero_shot"
    # `metadata_classification_few_shot`: uses few-shot (AI) technique to perform metadata classification
    PIPELINE_METADATA_CLASSIFICATION_FEW_SHOT = "metadata_classification_few_shot"


class MetadataClassificationFewShot(BaseModel):
    """
    Configuration for few-shot metadata classification.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    # Pre-trained model to use
    base_model: Optional[str] = "sentence-transformers/paraphrase-mpnet-base-v2"
    few_shot_classification_file: Optional[str] = (
        "./metadata_classification/data/observability_metrics_classification_zero_shot.json"
    )  # File containing few-shot classification external data
    few_shot_pretrained_model_directory: Optional[str] = (
        "./metadata_classification/data/few_shot_pretrained_model"
    )  # Directory containing a pretrained few-shot model


class MetadataClassificationZeroShot(BaseModel):
    """
    Configuration for zero-shot metadata classification.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    model: Optional[str] = "roberta-large-mnli"  # Pre-trained model to use
    zero_shot_classification_file: Optional[str] = (
        "./metadata_classification/data/observability_metrics_classification_zero_shot.json"
    )  # File containing zero-shot classification external data


class MetadataClassificationRegEx(BaseModel):
    """
    Configuration for regex metadata classification.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    regex_classification_file: Optional[str] = (
        "./metadata_classification/data/observability_metrics_classification_regex.json"
    )  # File containing regex classification external data


class IngestSubType(Enum):
    """
    Enumerates different subtypes for ingestion.
    """
    PIPELINE_INGEST_DUMMY = "dummy"
    PIPELINE_INGEST_FILE = "file"
    PIPELINE_INGEST_PROMQL = "promql"
    PIPELINE_INGEST_SERIALIZED = "serialized"


class IngestFormat(Enum):
    """
    Enumerates different subtypes for ingestion.
    """
    PIPELINE_INGEST_FORMAT_PROM = "prometheus"
    PIPELINE_INGEST_FORMAT_INSTANA_INFRA = "instana_infra"
    PIPELINE_INGEST_FORMAT_INSTANA_APP = "instana_app"


class EncodeSubType(Enum):
    """
    Enumerates different subtypes for encoding.
    """
    PIPELINE_ENCODE_SERIALIZED = "serialized"


class ExtractSubType(Enum):
    """
    Enumerates different subtypes for metadata extraction.
    """
    PIPELINE_EXTRACT_TSFEL = "tsfel"
    PIPELINE_EXTRACT_TRIM = "trim"  # trim time series


class ConfigGeneratorSubType(Enum):
    """
    Enumerates different subtypes for configuration generation.
    """
    PIPELINE_CONFIG_GENERATOR_NONE = "none"
    PIPELINE_CONFIG_GENERATOR_OTEL = "otel"
    PIPELINE_CONFIG_GENERATOR_OTEL_PROCESSOR = "otel_processor"
    PIPELINE_CONFIG_GENERATOR_PROCESSOR = "processor"


class GenerateInsightsType(Enum):
    """
    Enumerates different types of insights generation methods.
    """
    INSIGHTS_SIMILARITY_METHOD_PEARSON = "pearson"
    INSIGHTS_SIMILARITY_METHOD_SPEARMAN = "spearman"
    INSIGHTS_SIMILARITY_METHOD_KENDALL = "kendall"
    INSIGHTS_SIMILARITY_METHOD_DISTANCE = "distance"


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


class IngestTimeUnit(Enum):
    """
    Enumerates different time units supported for time series data
    """
    PIPELINE_TIME_UNIT_SECOND = "s"
    PIPELINE_TIME_UNIT_MILLISECOND = "ms"
    PIPELINE_TIME_UNIT_MICROSECOND = "us"


class IngestFile(BaseModel):
    """
    ### Configuration for file ingestion.
    This configuration is applied when `stage`:
      type: ingest
      subtype: file
    """
    model_config = ConfigDict(extra='forbid')
    file_name: str  # Name of the file to ingest
    filter_metadata: Optional[str] = ""  # Metadata filter
    ingest_name_template: Optional[str] = ""  # Template for ingest names
    format: Optional[str] = IngestFormat.PIPELINE_INGEST_FORMAT_PROM.value
    time_unit: Optional[str] = IngestTimeUnit.PIPELINE_TIME_UNIT_SECOND.value


class IngestSerialized(BaseModel):
    """
    ### Configuration for serialized file ingestion.
    This configuration is applied when `stage`:
      type: ingest
      subtype: serialized
    """
    model_config = ConfigDict(extra='forbid')
    file_name: str  # Name of the file to ingest


class IngestPromql(BaseModel):
    """
    Configuration for PromQL ingestion.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    url: str  # URL to fetch data from
    ingest_window: str  # Time interval for ingestion
    filter_metadata: Optional[str] = ""  # Metadata filter
    ingest_name_template: Optional[str] = ""  # Template for ingest names


class IngestDummy(BaseModel):
    """
    Configuration for dummy ingestion.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model


class EncodeSerialized(BaseModel):
    """
    ### Configuration for serialized file encoding.
    This configuration is applied when `stage`:
      type: encode
      subtype: serialized
    """
    model_config = ConfigDict(extra='forbid')
    file_name: str  # Name of the file to ingest


class FeatureExtractionTsfel(BaseModel):
    """
    Configuration for feature extraction using TSFEL.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    features_json_file: Optional[str] = \
        "extract/tsfel_conf/limited_statistical.json"  # JSON file for features
    resample_rate: Optional[str] = "30s"  # Resampling rate
    sampling_frequency: Optional[float] = (1 / 30)  # Sampling frequency
    trim: Optional[bool] = False


class InsightsAnalysisChainType(Enum):
    """
    Enumerates analysis processes (used by insights analysis_chain)
    """
    INSIGHTS_ANALYSIS_ZERO_VALUES = "zero_values"
    INSIGHTS_ANALYSIS_FIXED_VALUES = "fixed_values"
    INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS = "pairwise_correlations"
    INSIGHTS_ANALYSIS_COMPOUND_CORRELATIONS = "compound_correlations"
    INSIGHTS_ANALYSIS_METADATA_CLASSIFICATION = "metadata_classification"
    INSIGHTS_ANALYSIS_ACCESS_LOG_INTERSECT = "access_log_intersect"
    INSIGHTS_ANALYSIS_ACCESS_LOG_INTERSECT_NOT_ACCESSED = "access_log_intersect_not_accessed"


class AnalysisChainProcess(BaseModel):
    """
    Configuration for each of the analysis processes.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    type: InsightsAnalysisChainType  # The type of analysis process
    filter_signals_by_tags: Optional[List[str]] = ""  # Filter signals to analyze by list of tags
    close_to_zero_threshold: Optional[float] = 0  # Threshold for close to zero analysis
    pairwise_similarity_threshold: Optional[float] = 0.95  # Threshold for pairwise similarity
    pairwise_similarity_method: Optional[str] = (
        GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_PEARSON.value)  # Method for pairwise similarity
    # The distance algorithm to use (scipy.spacial.distance) when using distance method
    pairwise_similarity_distance_method: Optional[str] = ""
    compound_similarity_threshold: Optional[float] = 0.99  # Threshold for compound similarity
    access_log_file: Optional[str] = None  # Access_log file


class GenerateInsights(BaseModel):
    """
    Configuration for generating insights.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    # chain of analysis processes to be executed to generate insights
    analysis_chain: List[AnalysisChainProcess] = [
        AnalysisChainProcess(
            type=InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value),
        AnalysisChainProcess(
            type=InsightsAnalysisChainType.INSIGHTS_ANALYSIS_FIXED_VALUES.value,
            filter_signals_by_tags=[InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value]),
        AnalysisChainProcess(
            type=InsightsAnalysisChainType.INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS.value,
            filter_signals_by_tags=[InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value,
                                    InsightsAnalysisChainType.INSIGHTS_ANALYSIS_FIXED_VALUES.value]),
        AnalysisChainProcess(
            type=InsightsAnalysisChainType.INSIGHTS_ANALYSIS_COMPOUND_CORRELATIONS.value,
            filter_signals_by_tags=[InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value,
                                    InsightsAnalysisChainType.INSIGHTS_ANALYSIS_FIXED_VALUES.value,
                                    InsightsAnalysisChainType.INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS.value]),
        AnalysisChainProcess(
            type=InsightsAnalysisChainType.INSIGHTS_ANALYSIS_METADATA_CLASSIFICATION.value),
    ]


class ConfigGeneratorOtel(BaseModel):
    """
    Configuration for OpenTelemetry (OTel) configuration generation.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    directory: Optional[str] = "/tmp"  # Directory to store configuration


class ConfigGeneratorProcessor(BaseModel):
    """
    Configuration for processor-based configuration generation.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    processor_id_template: Optional[str] = ""  # Template for processor ID
    signal_name_template: Optional[str] = ""  # Template for signal name
    # Template for signal condition
    signal_condition_template: Optional[str] = ""
    signal_filter_template: Optional[str] = ""  # Template for signal filter
    directory: Optional[str] = None  # Directory to store configuration
    url: Optional[str] = None  # URL to fetch data from


class ConfigGeneratorOtelProcessor(BaseModel):
    """
    Configuration for otel processor-based configuration generation.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    processor_id_template: Optional[str] = ""  # Template for processor ID
    signal_name_template: Optional[str] = ""  # Template for signal name
    # Template for signal condition
    signal_condition_template: Optional[str] = ""
    signal_filter_template: Optional[str] = ""  # Template for signal filter
    directory: Optional[str] = None  # Directory to store configuration
    url: Optional[str] = None  # URL to fetch data from


class GeneratorNone(BaseModel):
    """
    Placeholder configuration for no specific generation task.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model


class MapSimple(BaseModel):
    """
    Configuration for simple map operations.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    number: int  # Number for mapping


class MapByName(BaseModel):
    """
    Configuration for map operations by name pattern.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    name_pattern: str  # Pattern for mapping by name


class ReduceSimple(BaseModel):
    """
    Configuration for simple reduce operations.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model


class BaseStageSchedule(BaseModel):
    """
    Configuration for order of stages that make up the pipeline.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    name: str  # Name of stage instance
    follows: Optional[List[str]] = []  # List of stages that must precede currently defined sage in the pipeline


class BaseStageParameters(BaseModel):
    """
    Configuration for Stage parameters.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    name: str  # Name of stage instance
    type: str  # Type of stage instance (e.g. ingest, extract, insights, etc)
    subtype: Optional[str] = None  # Subtype of stage instance (e.g. file_ingest vs promql ingest)
    input_data: Optional[List[str]] = []  # List of input data names for the stage
    output_data: Optional[List[str]] = []  # List of output data names for the stage
    cache_directory: Optional[str] = None  # Directory to store output data
    config: Optional[dict] = {}  # Stage-specific configuration parameters


class GlobalSettings(BaseModel):
    """
    Configuration for global settings.
    """
    model_config = ConfigDict(extra='forbid')  # Configuration for the model
    number_of_workers: Optional[int] = 0  # Number of processes to create to perform map-reduce operations in parallel


class PipelineDefinition(BaseModel):
    """
    Configuration for pipeline definition.
    """
    global_settings: Optional[dict] = {}
    pipeline: List[BaseStageSchedule]  # Order of stages that make up the pipeline
    parameters: List[BaseStageParameters]  # Specific parameters to configure each stage in the pipeline
