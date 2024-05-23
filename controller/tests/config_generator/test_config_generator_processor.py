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
from common.signal import Signals

expected_processor_generated_empty_content = """
rules:
"""


class TestGenerate:

    def test_config_generator_processor(self):
        config_generator_processor_config = ConfigGeneratorProcessor(directory="/tmp/test")
        extracted_signals = Signals()
        extracted_signals.metadata["ingest_source"] = "test"
        generate(config_generator_processor_config, extracted_signals, [], [])

        filename = config_generator_processor_config.directory + "/test/processor_filter_processor_config.yaml"

        # read the file and check if it contains the expected content
        with open(filename, "r") as f:
            assert f.read() == expected_processor_generated_empty_content
