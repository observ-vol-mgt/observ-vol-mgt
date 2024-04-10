import pytest
from unittest.mock import patch

time_series_type1 = [1, 2, 3, 4, 5]
time_series_type2 = [6, 7, 8, 9, 10]


@pytest.fixture
def input_file(tmpdir):
    # Create a temporary input file with json test data
    input_data = """\
[
    {"type": "type1", "time_series": [1,2,3,4,5]},
    {"type": "type2", "time_series": [6,7,8,9,10]}
]
"""
    input_file_path = tmpdir.join("file_ingest_test_input.txt")
    with open(input_file_path, 'w') as f:
        f.write(input_data)
    return input_file_path


def test_ingest(input_file):
    with patch("common.conf.get_configuration") as mocked_get_configuration:
        mocked_get_configuration.return_value = {'ingest_file': input_file}

        from ingest.file_ingest import ingest
        signals = ingest()

    assert signals[0].type == "type1"
    assert signals[0].time_series == time_series_type1
    assert signals[1].type == "type2"
    assert signals[1].time_series == time_series_type2

