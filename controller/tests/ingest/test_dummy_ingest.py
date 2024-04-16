import pytest
from unittest.mock import patch


def test_ingest():
    from ingest.dummy_ingest import ingest
    signals = ingest()

    assert signals[0].type == "metric"
    assert signals[0].time_series == {'time': [1, 2, 3], 'values': [10, 20, 30]}
