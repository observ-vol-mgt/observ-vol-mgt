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

from config_generator.config_generator import config_generator


def test_returns_not_generating_configuration_when_config_generator_type_is_none(mocker):
    # Mock the get_configuration function to return a configuration with config_generator_type set to "none"
    mocked_config = mocker.patch("config_generator.config_generator.get_configuration")
    mocked_config.return_value.config_generator_type = "none"

    # Call the config_generator function
    result = config_generator([], [], [])

    # Assert that the result is "not generating configuration"
    assert result == "not generating configuration"
