import re
from unittest.mock import patch
import requests
import requests_mock

time_series_type1 = ["7"]
time_series_type2 = ["7"]


def test_ingest():
    with patch("common.conf.get_configuration") as mocked_get_configuration:
        mocked_get_configuration.return_value = {'ingest_url': "https://localhost:8000/data", 'ingest_window': "10s"}
        with requests_mock.Mocker() as mocker:
            mocker.get(re.compile('https://localhost:8000/data/api/v1/label/__name__/values'),
                       json={"data": ["metric1", "metric2"]})
            mocker.get(re.compile('https://localhost:8000/data/api/v1/query*'),
                       json={"data": {"result": "7"}})
            from ingest.promql_ingest import ingest
            signals = ingest()

    assert signals[0].type == "metric"
    assert signals[0].time_series == time_series_type1
    assert signals[1].type == "metric"
    assert signals[1].time_series == time_series_type2
