# Config

Configuration of the pipeline stages is implemented via a yaml file.
The 'pipeline' section of the yaml file specifies the order in which to run the stages.
The 'parameters' section of the yaml file specifies the particular parameters for each of the stages.
Each stage has a name, and the names must match between the 'pipeline' and 'parameters' sections.

Standard field names for each stage are:
- name
- type (e.g. ingest, extract, insights)
- subtype (e.g. file ingest, promql ingest)
- input_data (list of input (lists))
- output_data (list of output (lists))
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

# Data Types

## Time Series
Time Series data is typically provided using the prometheus model with the following fields:
```
{
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
                {
                    "metric": {
                        "__name__": "commit_latency_ms",
                        "instance": "02:00:06:ff:fe:4b:b5:ac",
                        "plugin": "ceph",
                        "label": "ceph",
                        "snapshotId": "T9Arslj9-1Y3UYv6biDGDizVqzI",
                        "job": "prometheus"
                        },
                    "values": [
                        [1715252491.0, 0.0], 
                        [1715252492.0, 0.0], 
                        ....
                        ]
                }
                .....
              ]
    }
}
```

The `metric` field contains various metadata, including the `__name__` of the metric being reported; other fields are optional.
The time series data are contained in the `values` field as a list of `<timestamp, value>` ordered pairs.

## Signal
`Signal` is an internal data type used to store time-series data. 
It stores the metadata provided in the `metric` field and the time-series provided in the `values` field.

## Signals
`Signals` is an internal data type used to store multiple objects of type `Signal`.
It has some internally defined metadata plus a list of `Signal` structures.

# Details about some types of stages

## Ingest
An `ingest`-type stage typically reads data from some external source.
The details of the external source (file location, url, security parameters) are provided in the `config` section of the stage parameters.
An `ingest` stage is expected to have no `input_data` (`input_data: []`).
An `ingest` type stage outputs a list containing a single element (of type `Signals`).

## Extract
An `extract`-type stage typically performs some kind of transformation or metadata generation on `Signals`.
The `input_data` should contain a single `Signals` element and the `output_data` should contain a single `Signals` element.
For example:
```commandline
- name: feature_extraction_tsfel
  type: extract
  subtype: tsfel
  input_data: [classified_signals]
  output_data: [extracted_signals]
```

## Map Reduce
A map_reduce stage takes some input, breaks it up into some number of pieces,
and then runs some computation (possibly in parallel) on each of the pieces.
The output of the `map` operation is a list of sublists.
Each sublist is provided to a different instance of the `compute`.
The `compute` part of a map_reduce stage takes a single sublist and outputs a single sublist.
The outputs of each of the computations are then collected by the `reduce` operation into a combined output.
The config of a map_reduce stage looks like the following:

```commandline
- name: parallel_extract_stage
  type: map_reduce
  input_data: [signals]
  output_data: [extracted_signals]
  config:
    map_function:
      name: map1
      type: map
      subtype: simple
      config:
        <any parameters needed to customize the map operation>
    compute_function:
      name: extract_in_parallel
      type: extract
      subtype: tsfel
      config:
        <any parameters needed to customize the compute operation>
    reduce_function:
      name: reduce1
      type: reduce
      subtype: simple
      config:
        <any parameters needed to customize the reduce operation>
```

All map_reduce `compute` operations are of the same structure.
A single list as input (of type Signals) and a single list as output (of type Signals).
These must be preregistered in the code base as valid map_reduce `compute` operations.
The `map` and `reduce` operations must likewise be preregistered in the code base as such operations.

The map_reduce operation may be performed in parallel on multiple processes.
This is achieved by specifying an additional configuration parameter under global_settings.

```
global_settings:
  number_of_workers: 8
```


