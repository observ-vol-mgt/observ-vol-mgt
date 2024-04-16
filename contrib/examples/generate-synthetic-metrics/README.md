# generate-synthetic-metrics

This folder holds code that generates a fixed static set of metrics in prometheus API format.
The code generates a json file with the metrics. That file can be ingested into the controller using file ingest.
The metrics are used for basic validation of the controller functionality based on simple predictable synthetic data.

To activate execute `python generate-synthetic-metrics.py`

Note: Inside the code there is a variable `plot` that is set statically to False. Changing the variable to True and 
re-running will cause in exposure of pyplot visualization of the metrics ( in a new window )


