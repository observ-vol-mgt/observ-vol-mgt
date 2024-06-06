from typing import Dict

processor_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["aggregate", "aggregate_over_metrics", "enrichment", "filter", "adaptive", "frequency", "adaptive_stateful", "drop"]},
        "id": {"type": "string"},
        "metrics": {"$ref": "#/components/schemas/Metric"}
    },
    "required": ["type", "id", "metrics"]
}

dag_node_schema = {
    "type": "object",
    "properties": {
        "node": {"type": "string"},
        "children": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["node", "children"]
}

metric_schema = {
    "type": "object",
    "properties": {
        "metric_name": {"type": "string"},
        "condition": {"type": "string"}
    },
    "required": ["metric_name", "condition"]
}

aggregate_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "function": {"type": "string"},
             "time_window": {"type": "string"}
         },
         "required": ["function", "time_window"]
         }
    ]
}

aggregate_over_metrics_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "function": {"type": "string"}
         },
         "required": ["function"]
         }
    ]
}

enrichment_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "enrich": {"type": "array", "items": {"type": "object"}}
         },
         "required": ["enrich"]
         }
    ]
}

filter_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "action": {"type": "string"}
         },
         "required": ["action"]
         }
    ]
}

adaptive_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "threshold": {"anyOf": [{"type": "integer"}, {"type": "number"}]}
         },
         "required": ["threshold"]
         }
    ]
}

frequency_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "interval": {"type": "string"}
         },
         "required": ["interval"]
         }
    ]
}

adaptive_stateful_metric_schema = {
    "allOf": [
        {"$ref": "#/components/schemas/Metric"},
        {"type": "object",
         "properties": {
             "function": {"type": "string"}
         },
         "required": ["function"]
         }
    ]
}

action_create_dag_schema = {
    "type": "object",
    "properties": {
        "action_type": {"type": "string", "enum": ["create_dag"]},
        "processors": {"type": "array", "items": {"$ref": "#/components/schemas/Processor"}},
        "dag": {"type": "array", "items": {"$ref": "#/components/schemas/DAGNode"}}
    },
    "required": ["action_type", "processors"]
}

action_delete_dag_schema = {
    "type": "object",
    "properties": {
        "action_type": {"type": "string", "enum": ["delete_dag"]}
    },
    "required": ["action_type"]
}

rule_schema = {
    "type": "object",
    "properties": {
        "rule_id": {"type": "string"},
        "processors": {"type": "array", "items": {"type": "string"}},
        "expr": {"type": "string"},
        "duration": {"type": "string"},
        "description": {"type": "string"},
        "firing_action": {
            "anyOf": [
                {"$ref": "#/components/schemas/ActionCreateDAG"},
                {"$ref": "#/components/schemas/ActionDeleteDAG"}
            ]
        },
        "resolved_action": {
            "anyOf": [
                {"$ref": "#/components/schemas/ActionCreateDAG"},
                {"$ref": "#/components/schemas/ActionDeleteDAG"}
            ]
        }
    },
    "required": ["rule_id", "processors", "expr", "duration", "firing_action", "resolved_action"]
}

rules_schema = {
    "type": "object",
    "properties": {
        "rules": {"type": "array", "items": {"$ref": "#/components/schemas/Rule"}}
    },
    "required": ["rules"]
}

processors_config_schema = {
    "type": "object",
    "properties": {
        "processors": {"type": "array", "items": {"$ref": "#/components/schemas/Processor"}},
        "dag": {"type": "array", "items": {"$ref": "#/components/schemas/DAGNode"}}
    },
    "required": ["processors", "dag"]
}

# Define a dictionary to hold all schemas
schemas: Dict[str, dict] = {
    'Processor': processor_schema,
    'DAGNode': dag_node_schema,
    'Metric': metric_schema,
    'AggregateMetric': aggregate_metric_schema,
    'AggregateOverMetricsMetric': aggregate_over_metrics_metric_schema,
    'EnrichmentMetric': enrichment_metric_schema,
    'FilterMetric': filter_metric_schema,
    'AdaptiveMetric': adaptive_metric_schema,
    'FrequencyMetric': frequency_metric_schema,
    'AdaptiveStatefulMetric': adaptive_stateful_metric_schema,
    'ActionCreateDAG': action_create_dag_schema,
    'ActionDeleteDAG': action_delete_dag_schema,
    'Rule': rule_schema,
    'Rules': rules_schema,
    'ProcessorsConfig': processors_config_schema
}

