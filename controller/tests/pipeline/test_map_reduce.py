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
- name: stage1
parameters:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
- name: stage2
  type: map_reduce
  input_data: [data1]
  output_data: [data2]
  config:
    map_function:
      name: map1
      type: map
      subtype: simple
      config:
        number: 3
    compute_function:
      name: extract_in_parallel
      type: extract
      subtype: tsfel
    reduce_function:
      name: reduce1
      type: reduce
      subtype: simple
- name: stage3
  type: insights
  subtype:
  input_data: [data2]
  output_data: [data3, data4, data5]
  config:
"""


def test_basic_map_reduce():
    build_config(config1)
    p = Pipeline()
    p.build_pipeline()
    assert p.stage_execution_order[0].base_stage.name == "stage1"
    assert p.stage_execution_order[2].base_stage.name == "stage3"


config_missing_param = """
pipeline:
- name: stage3
  follows: [stage2]
- name: stage2
  follows: [stage1]
- name: stage1
parameters:
- name: stage1
  type: ingest
  subtype: file
  input_data: []
  output_data: [data1]
  config:
    file_name: dummy_file.txt
- name: stage2
  type: map_reduce
  input_data: [data1]
  output_data: [data2]
  config:
    map_function:
      name: map1
      type: map
      subtype: simple
      config:
        number: 3
    compute_function:
      name: extract_in_parallel
      type: extract
    reduce_function:
      name: reduce1
      type: reduce
      subtype: simple
- name: stage3
  type: insights
  subtype:
  input_data: [data2]
  output_data: [data3, data4, data5]
  config:
"""


def test_bad_map_reduce():
    build_config(config_missing_param)

    try:
        p = Pipeline()
        p.build_pipeline()
    except Exception as e:
        raise e
