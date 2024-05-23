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
from common.configuration_api import IngestFile

time_series_type1 = [[10, '1'], [20, '2'], [30, '3']]


@pytest.fixture
def input_file(tmpdir):
    # Create a temporary input file with json tests data
    input_data = """\
{
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {
          "__name__": "fake_same_a_1"
        },
        "values": [
          [
            10,
            "1"
          ],
          [
            20,
            "2"
          ],
          [
            30,
            "3"
          ]
        ]
      }
    ]
  }
}
"""
    input_file_path = tmpdir.join("file_ingest_test_input.txt")
    with open(input_file_path, 'w') as f:
        f.write(input_data)
    return input_file_path


def test_ingest(input_file):
    ingest_config = IngestFile(file_name=str(input_file))
    from ingest.file_ingest import ingest
    signals = ingest(ingest_config)

    assert signals[0].type == "metric"
    assert signals[0].time_series == time_series_type1
