# PMF: Programmable Metric Flows

PMF provides a mechanism to perform various transformation to the metrics flows to manage the volume of metrics and support various edge deployment usecases.
The current implementation supports transformation of metrics defined in prometheus format, where each metric comprises of metrics name and a set of labels in the form of key:value. PMF supports multiple transformation of metrics which can be represented as a DAG.
