from typing import List, Optional, Literal, Union
from pydantic import BaseModel, validator

class Metric(BaseModel):
    metric_name: str
    condition: str

class AggregateMetric(Metric):
    function: str
    time_window: str

class AggregateOverMetricsMetric(Metric):
    function: str

class EnrichValue(BaseModel):
    label_name: str
    label_value: str

class EnrichmentMetric(Metric):
    enrich: List[dict]

class FilterMetric(Metric):
    action: str

class AdaptiveMetric(Metric):
    threshold: Union[int, float]

class FrequencyMetric(Metric):
    interval: str

class AdaptiveStatefulMetric(Metric):
    function: str

class Processor(BaseModel):
    type: Literal["aggregate", "aggregate_over_metrics", "enrichment", "filter", "adaptive", "frequency", "adaptive_stateful", "drop"]
    id: str
    metrics: Union[AggregateMetric, AggregateOverMetricsMetric, EnrichmentMetric, FilterMetric, AdaptiveMetric, FrequencyMetric, AdaptiveStatefulMetric, Metric]

class DAGNode(BaseModel):
    node: str
    children: List[str]

class ProcessorsConfig(BaseModel):
    processors: List[Processor]
    dag: List[DAGNode]
