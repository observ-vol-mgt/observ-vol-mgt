#  Copyright 2024 IBM, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import pytest
import yaml
from common.conf import set_configuration, set_configuration
from common.pipeline import build_pipeline

def build_config(yaml_string):
    configuration = yaml.load(yaml_string)
    set_configuration(configuration)

config1 = """\
pipeline:
- name: ingest_file
- name: feature_extraction_tsfel
  follows: [ingest_file]
- name: generate_insights
  follows: [feature_extraction_tsfel]
- name: config_generator_otel
  follows: [feature_extraction_tsfel, generate_insights]
parameters:
- name: ingest_file
  type: ingest
  subtype: file
  input_data: []
  output_data: [signals]
  config:
    file_name: ../contrib/examples/generate-synthetic-metrics/time_series_data.json
- name: feature_extraction_tsfel
  type: extract
  subtype: tsfel
  input_data: [signals]
  output_data: [extracted_signals]
  config:
- name: generate_insights
  type: insights
  subtype:
  input_data: [extracted_signals]
  output_data: [signals_to_keep, signals_to_reduce, text_insights]
  config:
- name: config_generator_otel
  type: config_generator
  subtype: otel
  input_data: [extracted_signals, signals_to_keep, signals_to_reduce]
  output_data: [r_value]
  config:
    directory: /tmp
"""

def test_build_pipeline():
    build_config(config1)

    build_pipeline()

    from common.pipeline import stage_execution_order

    assert stage_execution_order[0].name == "ingest_file"
    assert stage_execution_order[2].name == "generate_insights"
