from common.signal import Signal, Signals


def ingest():
    signals = Signals()

    signals.metadata["ingest_type"] = "dummy"
    signals.metadata["ingest_source"] = "dummy_source"

    signals.append(Signal(type="metric", time_series={'time': [1, 2, 3], 'values': [10, 20, 30]}))

    return signals
