# Metric Generation

For local testing of the system we use a metric generator. The current version generates metrics in the prometheus formats comprising of a time series for each metric. Each metric is represented as set of labels and values. 
The generator can be used to generate fake metrics as well as custom  metrics with user provided labels names. 

## Random Metric Value
If the value of the metric value is not critical for the testing we can use the default mode to send the metrics.

## Metric Value with a patter

