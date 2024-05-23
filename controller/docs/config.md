# Config

Configuration of the pipeline stages is implemented via a yaml file.
The 'pipeline' section of the yaml file specifies the order in which to run the stages.
The 'parameters' section of the yaml file specifies the particular parameters for each of the stages.
Each stage has a name, and the names must match between the 'pipeline' and 'parameters' sections.

Standard field names for each stage are:
- name
- type (e.g. ingest, extract, insights)
- subtype (e.g. file ingest, promql ingest)
- input_data_types (list of lists)
- output_data_types (list of lists)
- config (configuration specific to this stage)

A sample config file might look like this:

```
pipeline:
- name: ingest_stage
- name: extract_stage
  follows: [ingest_stage]
- name: insights_stage
  follows: [extract_stage]
parameters:
- name: ingest_stage
  type: ingest
  subtype: file
  input_data: []
  output_data: [signals]
  config:
    file_name: <../some_file.json>
- name: extract_stage
  type: extract
  subtype: <some extract subtype>
  input_data: [signals]
  output_data: [extracted_signals]
  config:
- name: insights_stage
  type: insights
  subtype: <some insights subtype>
  input_data: [extracted_signals]
  output_data: [text_insights]
  config:
```

A stage may follow multiple other stages, and may receive input from multiple earlier stages.

