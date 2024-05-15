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

import re
from unittest.mock import patch

import requests_mock

time_series_type1 = ["7"]
time_series_type2 = ["7"]


def test_ingest():
    ingest_config = {
        "url": "https://localhost:8000/data",
        "window": "10s"
    }

    with patch("common.conf.get_configuration") as mocked_get_configuration:
        mocked_get_configuration.return_value = {'ingest_url': "https://localhost:8000/data", 'ingest_window': "10s"}
        with requests_mock.Mocker() as mocker:
            mocker.get(re.compile('https://localhost:8000/data/api/v1/label/__name__/values'),
                       json={"data": ["metric1", "metric2"]})
            mocker.get(re.compile('https://localhost:8000/data/api/v1/query*'),
                       json={"data": {"result": "7"}})
            from ingest.promql_ingest import ingest
            signals = ingest(ingest_config)

    assert signals[0].type == "metric"
    assert signals[0].time_series == time_series_type1
    assert signals[1].type == "metric"
    assert signals[1].time_series == time_series_type2
