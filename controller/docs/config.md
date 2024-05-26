# Config

Configuration of the pipeline stages is implemented via a yaml file.
The 'pipeline' section of the yaml file specifies the order in which to run the stages.
The 'parameters' section of the yaml file specifies the particular parameters for each of the stages.
Each stage has a name, and the names must match between the 'pipeline' and 'parameters' sections.

Standard field names for each stage are:
- name
- type (e.g. ingest, split, transform, merge, extract, insights)
- subtype (e.g. file ingest, promql ingest)
- input_data (list of inputs)
- output_data (list of outputs)
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

# Special types of stages

## Split, Compute, Merge

A splitter stage takes a single list of elements as input and divides it into some number of output lists.
Each output list is then provided as input to a separate copy of a specified compute (or transform) stage.
Each such (identical) compute/transform stage returns a list of a list as output, which are provided as input to a merge stage.
This can be thought as similar to the map-reduce model.
Each intermediate compute/transform stage must be specified with `multi_stage: True` as one of the coniguration parameters.
Each intermediate compute/transform stage is provided a single input list from its previous stage
and should output a single list to its next stage.

