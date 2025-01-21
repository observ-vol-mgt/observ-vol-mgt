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


## Insights
An `insights` stage performs the analytics on the data.
The `input_data` should contain a single `Signals` element (typically after feature extraction)
and the `output_data`  contains 3 lists: [signals_to_keep, signals_to_reduce, text_insights].

The following insights are currently supported:
- zero_values: identify signals that have constant zero value.
- fixed_values: identify signals that have constant non-zero value.
- monotonic: identify signals that are monotonic (typical of a counter)
- pairwise_correlations: identify signals that are directly correlated to some other signal.
- compound_correlations: identify signals that are some linear combination of other signals.

The order of the computed analytics should be specified.
It is expected that typically the zero-valued and fixed-valued signals are identified,
and then the remaining signals are tested for monotonicity or correlation.

The zero-valued, fixed-valued, and correlated signals are primary candidates to be dropped.
The monotonic signals are primary candidates to have their measurement frequency reduced.

The format of the `insights` stage is as follows:
```commandline
- name: generate_insights
  type: insights
  subtype:
  input_data: [extracted_signals]
  output_data: [signals_to_keep, signals_to_reduce, text_insights]
  config:
    analysis_chain:
    - type: zero_values
      close_to_zero_threshold: 0.02
    - type: fixed_values
      filter_signals_by_tags: ["zero_values"]
    - type: monotonic
      filter_signals_by_tags: ["zero_values","fixed_values"]
    - type: pairwise_correlations
      filter_signals_by_tags: ["zero_values","fixed_values"]
      pairwise_similarity_threshold: 0.02
      pairwise_similarity_distance_method: pearson
    - type: compound_correlations
      filter_signals_by_tags: ["zero_values","fixed_values","pairwise_correlations"]
      compound_similarity_threshold: 1
```

Any subset of the available analytics may be specified in the `analytics_chain`.

The `filter_signals_by_tags` key specifies which signals to exclude from the particular analysis stage.
Thus, we do not include the zero-valued and fixed-valued signals in the pairwise-correlation analytic.
Additional parameters are availabe for some of the analytics.

These insights can be viewed in the `controller` gui (in the demo see http://localhost:5000/insights).


## Config_generator
The `config_generator` stage takes the data proviced by the `insights` stage and produces yaml files to configure
the metrics collector to utilize the inisights.
The `input_data` should contain 3 lists of signals: [extracted_signals, signals_to_keep, signals_to_reduce].

The format of the `config_generator` stage is as follows:
```commandline
- name: config_generator_processor
  type: config_generator
  subtype: pmf_processor
  input_data: [extracted_signals, signals_to_keep, signals_to_reduce]
  output_data: [r_value]
  config:
    signal_filter_reduce_template: "k8s_|nwdaf_|process_"
    signal_filter_adjust_template: "k8s_|nwdaf_|process_"
    signal_name_template: "$original_name"
    signal_condition_template: "cluster=$cluster and instance=$instance"
    processor_id_template: "$processor"
    directory: /tmp
    url: http://manager:5010
```

The `signal_filter_reduce_template` parameter contains a regular expression of metric names that interest us.
Metrics whose names do not match the `signal_filter_reduce_template` are ignored when computing the list of metrics to reduce.
Similarly, metrics whose names do not match the `signal_filter_adjust_template` are ignored when computing the list of metrics whose sampling frequency to adjust.
The `url` parameter specifies where to send the produced generated configurations.
The `directory` parameter may be used to specify where to save (locally) a copy of the generated configuration files.

We support both PMF (`subtype: pmf_processor`) and otel (`subtype: otel_processor`) formats.

To specify a customized metric frequency for counters (when using otel), the following parameter can be used:

```commandline
  config:
    counter_default_interval: 30s
```

To specify a specific sampling frequency for specified metrics, the following config parameters may be used:
```commandline
  config:
    metrics_adjustment:
    - name_template: process_
      interval: 20s
    - name:_template k8s_pod_
      interval: 10s
```
These `name_template:` parameters match a regular expression of metric names.
In this example, all metrics whose names contain `process_` will have their metrics reporting adjusted to every 20s.

These can be combined into a configuration that looks like this:
```commandline
  config:
    signal_filter_reduce_template: "k8s_|nwdaf_|process_"
    signal_filter_adjust_template: "k8s_|nwdaf_|process_"
    signal_name_template: "$original_name"
    signal_condition_template: "resource.attributes[\"processor\"] == \"$processor\" and resource.attributes[\"instance\"] == \"$instance\""
    processor_id_template: "$processor"
    counter_default_interval: 30s
    metrics_adjustment:
    - name_template: process_
      interval: 20s
    - name_template: k8s_
      interval: 10s
    - name_template: .*
      tag_filter: ["monotonic"]
      interval: 30s
    directory: /tmp
    url: http://manager:5010
```
The `name_template: .*` matches all regular expressions, and may be used to catch all other metrics that are not explicitly specified earlier.
The rules for `metrics_adjustment` are imposed on a first-match basis.
The `tag_filter` parameter specifies a list of tags to be checked to restrict the application of the `metrics_adjustment` rule.
In this example, only those signals that contain a tag `monotonic` will match this catch-all `name_template` and have their sampling frequency adjusted to 30 seconds.

