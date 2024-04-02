from common.signal import Signal
from common.conf import get_configuration
import json

signals = []


def ingest():
    conf = get_configuration()
    ingest_file = conf["ingest_file"]
    print(ingest_file)
    try:
        with open(ingest_file, 'r') as file:
            json_signals = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e

    for json_signal in json_signals:
        signals.append(Signal(type=json_signal["type"],
                              time_series=json_signal["time_series"]))

    return signals
