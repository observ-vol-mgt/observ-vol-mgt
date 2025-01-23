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

import yaml
from common.conf import set_configuration
from workflow_orchestration.pipeline import Pipeline


def build_config(yaml_string):
    configuration = yaml.load(yaml_string, Loader=yaml.FullLoader)
    set_configuration(configuration)


config1 = """
pipeline:
- name: stage3
  follows: [stage2]
- name: stage2
  follows: [stage1]
- name: stage4
  follows: [stage2, stage3]
- name: stage1
parameters:
- name: stage4
  type: config_generator
  subtype: otel
  input_data: [data2, data3, data4]
  output_data: [data6]
  config:
    directory: /tmp
- name: stage2
  type: extract
  subtype: tsfel
  input_data: [data1]
  output_data: [data2]
  config:
- name: stage3
  type: insights
  subtype:
  input_data: [data2]
  output_data: [data3, data4, data5]
  config:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
"""


def test_build_pipeline():
    build_config(config1)
    p = Pipeline()
    p.build_pipeline()

    assert p.stage_execution_order[0].base_stage.name == "stage1"
    assert p.stage_execution_order[2].base_stage.name == "stage3"


config_multiple_initial = """
pipeline:
- name: stage1
- name: stage2
  follows: [stage1]
- name: stage3
parameters:
- name: stage2
  type: extract
  subtype: tsfel
  input_data: [data1]
  output_data: [data2]
  config:
- name: stage3
  type: ingest
  subtype: none
  input_data: []
  output_data: [data3, data4, data5]
  config:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
"""


def test_multiple_initial():
    build_config(config_multiple_initial)

    try:
        p = Pipeline()
        p.build_pipeline()
        assert False
    except Exception:
        assert True


config_follows_missing = """
pipeline:
- name: stage1
- name: stage2
  follows: [stage3]
parameters:
- name: stage2
  type: extract
  subtype: tsfel
  input_data: [data1]
  output_data: [data2]
  config:
- name: stage3
  type: ingest
  subtype: none
  input_data: []
  output_data: [data3, data4, data5]
  config:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
"""


def test_follows_missing():
    build_config(config_follows_missing)
    try:
        p = Pipeline()
        p.build_pipeline()
        assert False
    except Exception:
        assert True


config_missing_params = """
pipeline:
- name: stage1
- name: stage2
  follows: [stage1]
parameters:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
"""


def test_missing_params():
    build_config(config_missing_params)
    try:
        p = Pipeline()
        p.build_pipeline()
        assert False
    except Exception:
        assert True


config_duplicate_stage = """
pipeline:
- name: stage1
- name: stage2
  follows: [stage1]
- name: stage3
parameters:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
- name: stage2
  type: extract
  subtype: tsfel
  input_data: [data1]
  output_data: [data2]
  config:
- name: stage3
  type: ingest
  subtype: none
  input_data: []
  output_data: [data3, data4, data5]
  config:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
"""


def test_duplicate_stage():
    build_config(config_multiple_initial)

    try:
        p = Pipeline()
        p.build_pipeline()
        assert False
    except Exception:
        assert True
