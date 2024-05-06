# observ-vol-mgt: Observability Volume Manager

Observability Volume Manager provides a mechanism to perform various transformations to the metrics flows to manage the volume of metrics and support various edge deployment use cases.
The current implementation supports transformation of metrics defined in Prometheus format, where each metric comprises of metrics name and a set of labels in the form of key:value. PMF supports multiple transformations of metrics which can be represented as a DAG.

## folders structure

### controller

The controller folder holds the code to centrally control the volume management

### contrib

The contrib folder holds various tools and scripts that helps to develop, build, and maintain the project
