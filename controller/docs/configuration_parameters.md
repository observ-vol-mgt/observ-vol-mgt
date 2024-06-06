# Table of Contents

* [common.configuration\_api](#common.configuration_api)
  * [StageType](#common.configuration_api.StageType)
    * [INGEST](#common.configuration_api.StageType.INGEST)
    * [FEATURES\_EXTRACTION](#common.configuration_api.StageType.FEATURES_EXTRACTION)
    * [INSIGHTS](#common.configuration_api.StageType.INSIGHTS)
    * [CONFIG\_GENERATOR](#common.configuration_api.StageType.CONFIG_GENERATOR)
    * [METADATA\_CLASSIFICATION](#common.configuration_api.StageType.METADATA_CLASSIFICATION)
    * [MAP\_REDUCE](#common.configuration_api.StageType.MAP_REDUCE)
  * [MetadataClassificationSubType](#common.configuration_api.MetadataClassificationSubType)
  * [MetadataClassificationZeroShot](#common.configuration_api.MetadataClassificationZeroShot)
    * [model\_config](#common.configuration_api.MetadataClassificationZeroShot.model_config)
    * [model](#common.configuration_api.MetadataClassificationZeroShot.model)
    * [zero\_shot\_classification\_file](#common.configuration_api.MetadataClassificationZeroShot.zero_shot_classification_file)
  * [IngestSubType](#common.configuration_api.IngestSubType)
  * [ExtractSubType](#common.configuration_api.ExtractSubType)
  * [ConfigGeneratorSubType](#common.configuration_api.ConfigGeneratorSubType)
  * [GenerateInsightsType](#common.configuration_api.GenerateInsightsType)
  * [MapSubType](#common.configuration_api.MapSubType)
  * [ReduceSubType](#common.configuration_api.ReduceSubType)
  * [IngestFile](#common.configuration_api.IngestFile)
    * [model\_config](#common.configuration_api.IngestFile.model_config)
    * [file\_name](#common.configuration_api.IngestFile.file_name)
    * [filter\_metadata](#common.configuration_api.IngestFile.filter_metadata)
    * [ingest\_name\_template](#common.configuration_api.IngestFile.ingest_name_template)
  * [IngestPromql](#common.configuration_api.IngestPromql)
    * [model\_config](#common.configuration_api.IngestPromql.model_config)
    * [url](#common.configuration_api.IngestPromql.url)
    * [ingest\_window](#common.configuration_api.IngestPromql.ingest_window)
    * [filter\_metadata](#common.configuration_api.IngestPromql.filter_metadata)
    * [ingest\_name\_template](#common.configuration_api.IngestPromql.ingest_name_template)
  * [IngestDummy](#common.configuration_api.IngestDummy)
    * [model\_config](#common.configuration_api.IngestDummy.model_config)
  * [FeatureExtractionTsfel](#common.configuration_api.FeatureExtractionTsfel)
    * [model\_config](#common.configuration_api.FeatureExtractionTsfel.model_config)
    * [features\_json\_file](#common.configuration_api.FeatureExtractionTsfel.features_json_file)
    * [resample\_rate](#common.configuration_api.FeatureExtractionTsfel.resample_rate)
    * [sampling\_frequency](#common.configuration_api.FeatureExtractionTsfel.sampling_frequency)
  * [FeatureExtractionTsfresh](#common.configuration_api.FeatureExtractionTsfresh)
    * [model\_config](#common.configuration_api.FeatureExtractionTsfresh.model_config)
  * [GenerateInsights](#common.configuration_api.GenerateInsights)
    * [model\_config](#common.configuration_api.GenerateInsights.model_config)
    * [pairwise\_similarity\_threshold](#common.configuration_api.GenerateInsights.pairwise_similarity_threshold)
    * [pairwise\_similarity\_method](#common.configuration_api.GenerateInsights.pairwise_similarity_method)
    * [compound\_similarity\_threshold](#common.configuration_api.GenerateInsights.compound_similarity_threshold)
  * [ConfigGeneratorOtel](#common.configuration_api.ConfigGeneratorOtel)
    * [model\_config](#common.configuration_api.ConfigGeneratorOtel.model_config)
    * [directory](#common.configuration_api.ConfigGeneratorOtel.directory)
  * [ConfigGeneratorProcessor](#common.configuration_api.ConfigGeneratorProcessor)
    * [model\_config](#common.configuration_api.ConfigGeneratorProcessor.model_config)
    * [processor\_id\_template](#common.configuration_api.ConfigGeneratorProcessor.processor_id_template)
    * [signal\_name\_template](#common.configuration_api.ConfigGeneratorProcessor.signal_name_template)
    * [signal\_condition\_template](#common.configuration_api.ConfigGeneratorProcessor.signal_condition_template)
    * [signal\_filter\_template](#common.configuration_api.ConfigGeneratorProcessor.signal_filter_template)
    * [directory](#common.configuration_api.ConfigGeneratorProcessor.directory)
    * [url](#common.configuration_api.ConfigGeneratorProcessor.url)
  * [GeneratorNone](#common.configuration_api.GeneratorNone)
    * [model\_config](#common.configuration_api.GeneratorNone.model_config)
  * [MapSimple](#common.configuration_api.MapSimple)
    * [model\_config](#common.configuration_api.MapSimple.model_config)
    * [number](#common.configuration_api.MapSimple.number)
  * [MapByName](#common.configuration_api.MapByName)
    * [model\_config](#common.configuration_api.MapByName.model_config)
    * [name\_pattern](#common.configuration_api.MapByName.name_pattern)
  * [ReduceSimple](#common.configuration_api.ReduceSimple)
    * [model\_config](#common.configuration_api.ReduceSimple.model_config)

<a id="common.configuration_api"></a>

# common.configuration\_api

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

<a id="common.configuration_api.StageType"></a>

## StageType

Stage `type` (stage functionality):  
Each `named stage configuration` includes one of the following `type` (string) options:

<a id="common.configuration_api.StageType.INGEST"></a>

#### INGEST

`ingest`: ingest data from various sources into the controller

<a id="common.configuration_api.StageType.FEATURES_EXTRACTION"></a>

#### FEATURES\_EXTRACTION

`extract`: performs feature extraction on the signals

<a id="common.configuration_api.StageType.INSIGHTS"></a>

#### INSIGHTS

`insights`: generates insights (analytics)

<a id="common.configuration_api.StageType.CONFIG_GENERATOR"></a>

#### CONFIG\_GENERATOR

`config_generator`: Generates and apply processor configurations

<a id="common.configuration_api.StageType.METADATA_CLASSIFICATION"></a>

#### METADATA\_CLASSIFICATION

`metadata_classification`: Metadata classification

<a id="common.configuration_api.StageType.MAP_REDUCE"></a>

#### MAP\_REDUCE

`map_reduce`: apply map reduce operations (for stages scalability)

<a id="common.configuration_api.MetadataClassificationSubType"></a>

## MetadataClassificationSubType

Enumerates subtypes for metadata classification.

<a id="common.configuration_api.MetadataClassificationZeroShot"></a>

## MetadataClassificationZeroShot

Configuration for zero-shot metadata classification.

<a id="common.configuration_api.MetadataClassificationZeroShot.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.MetadataClassificationZeroShot.model"></a>

#### model

Pre-trained model to use

<a id="common.configuration_api.MetadataClassificationZeroShot.zero_shot_classification_file"></a>

#### zero\_shot\_classification\_file

File containing zero-shot classification data

<a id="common.configuration_api.IngestSubType"></a>

## IngestSubType

Enumerates different subtypes for ingestion.

<a id="common.configuration_api.ExtractSubType"></a>

## ExtractSubType

Enumerates different subtypes for metadata extraction.

<a id="common.configuration_api.ConfigGeneratorSubType"></a>

## ConfigGeneratorSubType

Enumerates different subtypes for configuration generation.

<a id="common.configuration_api.GenerateInsightsType"></a>

## GenerateInsightsType

Enumerates different types of insights generation methods.

<a id="common.configuration_api.MapSubType"></a>

## MapSubType

Enumerates different subtypes for map operations.

<a id="common.configuration_api.ReduceSubType"></a>

## ReduceSubType

Enumerates different subtypes for reduce operations.

<a id="common.configuration_api.IngestFile"></a>

## IngestFile

Configuration for file ingestion.

<a id="common.configuration_api.IngestFile.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.IngestFile.file_name"></a>

#### file\_name

Name of the file to ingest

<a id="common.configuration_api.IngestFile.filter_metadata"></a>

#### filter\_metadata

Metadata filter

<a id="common.configuration_api.IngestFile.ingest_name_template"></a>

#### ingest\_name\_template

Template for ingest names

<a id="common.configuration_api.IngestPromql"></a>

## IngestPromql

Configuration for PromQL ingestion.

<a id="common.configuration_api.IngestPromql.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.IngestPromql.url"></a>

#### url

URL to fetch data from

<a id="common.configuration_api.IngestPromql.ingest_window"></a>

#### ingest\_window

Time interval for ingestion

<a id="common.configuration_api.IngestPromql.filter_metadata"></a>

#### filter\_metadata

Metadata filter

<a id="common.configuration_api.IngestPromql.ingest_name_template"></a>

#### ingest\_name\_template

Template for ingest names

<a id="common.configuration_api.IngestDummy"></a>

## IngestDummy

Configuration for dummy ingestion.

<a id="common.configuration_api.IngestDummy.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.FeatureExtractionTsfel"></a>

## FeatureExtractionTsfel

Configuration for feature extraction using TSFEL.

<a id="common.configuration_api.FeatureExtractionTsfel.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.FeatureExtractionTsfel.features_json_file"></a>

#### features\_json\_file

JSON file for features

<a id="common.configuration_api.FeatureExtractionTsfel.resample_rate"></a>

#### resample\_rate

Resampling rate

<a id="common.configuration_api.FeatureExtractionTsfel.sampling_frequency"></a>

#### sampling\_frequency

Sampling frequency

<a id="common.configuration_api.FeatureExtractionTsfresh"></a>

## FeatureExtractionTsfresh

Configuration for feature extraction using TSFRESH.

<a id="common.configuration_api.FeatureExtractionTsfresh.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.GenerateInsights"></a>

## GenerateInsights

Configuration for generating insights.

<a id="common.configuration_api.GenerateInsights.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.GenerateInsights.pairwise_similarity_threshold"></a>

#### pairwise\_similarity\_threshold

Threshold for pairwise similarity

<a id="common.configuration_api.GenerateInsights.pairwise_similarity_method"></a>

#### pairwise\_similarity\_method

Method for pairwise similarity

<a id="common.configuration_api.GenerateInsights.compound_similarity_threshold"></a>

#### compound\_similarity\_threshold

Threshold for compound similarity

<a id="common.configuration_api.ConfigGeneratorOtel"></a>

## ConfigGeneratorOtel

Configuration for OpenTelemetry (OTel) configuration generation.

<a id="common.configuration_api.ConfigGeneratorOtel.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.ConfigGeneratorOtel.directory"></a>

#### directory

Directory to store configuration

<a id="common.configuration_api.ConfigGeneratorProcessor"></a>

## ConfigGeneratorProcessor

Configuration for processor-based configuration generation.

<a id="common.configuration_api.ConfigGeneratorProcessor.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.ConfigGeneratorProcessor.processor_id_template"></a>

#### processor\_id\_template

Template for processor ID

<a id="common.configuration_api.ConfigGeneratorProcessor.signal_name_template"></a>

#### signal\_name\_template

Template for signal name

<a id="common.configuration_api.ConfigGeneratorProcessor.signal_condition_template"></a>

#### signal\_condition\_template

Template for signal condition

<a id="common.configuration_api.ConfigGeneratorProcessor.signal_filter_template"></a>

#### signal\_filter\_template

Template for signal filter

<a id="common.configuration_api.ConfigGeneratorProcessor.directory"></a>

#### directory

Directory to store configuration

<a id="common.configuration_api.ConfigGeneratorProcessor.url"></a>

#### url

URL to fetch data from

<a id="common.configuration_api.GeneratorNone"></a>

## GeneratorNone

Placeholder configuration for no specific generation task.

<a id="common.configuration_api.GeneratorNone.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.MapSimple"></a>

## MapSimple

Configuration for simple map operations.

<a id="common.configuration_api.MapSimple.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.MapSimple.number"></a>

#### number

Number for mapping

<a id="common.configuration_api.MapByName"></a>

## MapByName

Configuration for map operations by name pattern.

<a id="common.configuration_api.MapByName.model_config"></a>

#### model\_config

Configuration for the model

<a id="common.configuration_api.MapByName.name_pattern"></a>

#### name\_pattern

Pattern for mapping by name

<a id="common.configuration_api.ReduceSimple"></a>

## ReduceSimple

Configuration for simple reduce operations.

<a id="common.configuration_api.ReduceSimple.model_config"></a>

#### model\_config

Configuration for the model

