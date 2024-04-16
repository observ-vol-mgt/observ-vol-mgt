# Metric Generation

For local testing of the system we use a metric generator. The current version generates metrics in the prometheus formats comprising of a time series for each metric. Each metric is represented as set of labels and values. 
The generator can be used to generate fake metrics as well as custom  metrics with user provided labels names. 

## Fake Metrics
If the value of the metric name is not critical for the testing we can use the default mode to send the metrics.
```
python3 gen-metrics-gutentag.py --fake --nmetrics 100 --nlabels 10
```
You can vary the number of metrics and labels using the `--nmetrics` and `--nlabels` parameters respectively.

## With a conf file

```
python3 gen-metrics-gutentag.py --conf conf.yaml --nmetrics 100 --nlabels 10
```
The current conf supports certain set of metric type such as as can be seen in t
