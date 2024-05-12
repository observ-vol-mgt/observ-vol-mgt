# Config

Configuration of the pipeline stages is implemented via a yaml file.
The 'pipeline' section of the yaml file specifies the order in which to run the stages.
The 'parameters' section of the yaml file specifies the particular parameters for each of the stages.
Each stage has a name, and the names must match between the 'pipeline' and 'parameters' sections.

Standard field names for each stage are:
- name
- type (e.g. ingest, extract, insights)
- subtype (e.g. file ingest, promql ingest)
- input_data_types (Signals, Text)
- output_data_types (Signals, Text)
- config (configuration specific to this stage)

A sample config file might look like this:

```
pipeline:
- name: ingest_file
- name: feature_extraction_tsfel
  follows: [ingest_file]
- name: generate_insights
  follows: [feature_extraction_tsfel]
- name: config_generator_otel
  follows: [feature_extraction_tsfel, generate_insights]
parameters:
- name: ingest_file
  type: ingest
  subtype: file
  input_data: []
  output_data: [signals]
  config:
    file_name: ../contrib/examples/generate-synthetic-metrics/time_series_data.json
- name: feature_extraction_tsfel
  type: extract
  subtype: tsfel
  input_data: [signals]
  output_data: [extracted_signals]
  config:
- name: generate_insights
  type: insights
  subtype:
  input_data: [extracted_signals]
  output_data: [signals_to_keep, signals_to_reduce, text_insights]
  config:
- name: config_generator_otel
  type: config_generator
  subtype: otel
  input_data: [extracted_signals, signals_to_keep, signals_to_reduce]
  output_data: [r_value]
  config:
```

