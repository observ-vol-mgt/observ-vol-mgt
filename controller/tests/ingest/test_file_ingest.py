import pytest
from unittest.mock import patch

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
    with patch("common.conf.get_configuration") as mocked_get_configuration:
        config = (lambda Config, ingest_file: Config(ingest_file))(
            type('Config', (), {'__init__': lambda self, ingest_file: setattr(self, 'ingest_file', ingest_file)}),
            input_file
        )
        mocked_get_configuration.return_value = config

        from ingest.file_ingest import ingest
        signals = ingest()

    assert signals[0].type == "metric"
    assert signals[0].time_series == time_series_type1
