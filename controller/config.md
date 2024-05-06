# Config

Configuration of the pipeline stages is implemented via a yaml file.
One section of the yaml file specifies the order in which to run the stages.
Another section of the yaml file specifies the particular parameters for each of the stages.

Standard field names for each stage are:
- name
- type (e.g. ingest, extract, insights)
- subtype (e.g. file ingest, promql ingest)
- input_data_type (TBD)
- output_data_type (TBD)
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
  input_data_type:
  output_data_type:
  config:
  - file_name: file
- name: feature_extraction
  type: extract
  subtype: tsfel
  input_data_type:
  output_data_type:
  config:
- name: generate_insights
  type: insights
  subtype:
  input_data_type:
  output_data_type:
  config:
```

