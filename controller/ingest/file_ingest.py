import logging
from common.signal import Signal
from common.conf import get_configuration
import json

logger = logging.getLogger(__name__)


def ingest():
    signals = []
    conf = get_configuration()
    ingest_file = conf.ingest_file
    logger.info(f"Reading signals from {ingest_file}")
    try:
        with open(ingest_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e
    json_signals = data["data"]["result"]
    for json_signal in json_signals:
        if 'metric' in json_signal.keys():
            signal_type = "metric"
            signal_metadata = json_signal["metric"]
            signal_time_series = json_signal["values"]
        else:
            raise Exception("Ingest: signal type - Not implemented")

        signals.append(Signal(type=signal_type,
                              metadata=signal_metadata,
                              time_series=signal_time_series))

    return signals
