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

from config_generator.config_generator_processor import generate

from common.configuration_api import ConfigGeneratorProcessor
from common.signal import Signal, Signals

expected_processor_generated_empty_content = """processors:
  - type: drop
    id: drop_0
    metrics:
      metric_name: name_test
      condition: condition_test
dag:
  - node: drop_0
    children: []"""


class TestGenerate:

    def test_config_generator_processor(self):
        config_generator_processor_config = ConfigGeneratorProcessor(directory="/tmp/test",
                                                                     processor_id_template="$processor",
                                                                     signal_name_template="$__name__",
                                                                     signal_condition_template="$condition"
                                                                     )
        extracted_signal = Signal("metric", {"processor": "p1",
                                             "_id": "id_test",
                                             "__name__": "name_test",
                                             "condition": "condition_test"})
        extracted_signals = Signals(
            {"ingest_source": "test"}, [extracted_signal])
        generate(config_generator_processor_config,
                 extracted_signals, [], ["name_test"])

        filename = config_generator_processor_config.directory + \
            "/p1/test/processor_filter_processor_config.yaml"

        # read the file and check if it contains the expected content
        with open(filename, "r") as f:
            text = f.read()
            assert text == expected_processor_generated_empty_content
