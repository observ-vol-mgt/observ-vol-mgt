from common.signal import Signal


def ingest():
    return Signal(type="metric", time_series={'time': [1, 2, 3], 'values': [10, 20, 30]})
