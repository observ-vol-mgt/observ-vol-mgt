# Config

Configuration of the pipeline stages is implemented via a yaml file.
One section of the yaml file specifies the order in which to run the stages.
Another section of the yaml file specifies the particular parameters for each of the stages.

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
- name: feature_extraction
  follows: ingest_file
- name: generate_insights
  follows: feature_extraction
parameters:
- name: ingest_file
  type: ingest
  subtype: file
  input_data_types: []
  output_data_types: [Signals]
  config:
    file_name: ../contrib/examples/generate-synthetic-metrics/time_series_data.json
- name: feature_extraction
  type: extract
  subtype: tsfel
  input_data_types: [Signals]
  output_data_types: [Signals]
  config:
- name: generate_insights
  type: insights
  subtype:
  input_data_types: [Signals]
  output_data_types: [Signals, Signals, Text]
  config:
```

