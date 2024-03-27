from common.signal import Signal
from common.conf import get_configuration
import json


def ingest():
    ingest_file = get_configuration().ingest_file
    try:
        with open(ingest_file, 'r') as file:
            signal = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e

    return Signal(type=signal.type, time_series=signal.time_series)
