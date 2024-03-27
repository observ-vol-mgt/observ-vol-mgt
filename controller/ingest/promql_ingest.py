from common.signal import Signal
from common.conf import get_configuration
from prometheus_api_client import PrometheusConnect
from datetime import timedelta
from prometheus_api_client.utils import parse_datetime

signals = []
signal_type = "metric"


def ingest():
    ingest_url = get_configuration()["ingest_url"]
    ingest_window = get_configuration()["ingest_window"]
    try:
        prom = PrometheusConnect(url=ingest_url, disable_ssl=True)
        metrics = prom.all_metrics()
        for metric in metrics:
            start_time = parse_datetime(ingest_window)
            end_time = parse_datetime("now")
            metric_data = prom.get_metric_range_data(
                metric,
                start_time=start_time,
                end_time=end_time,
            )
            signals.append(Signal(type=signal_type, time_series=metric_data))

    except Exception as e:
        err = f"The url {ingest_url} does not exist {e}"
        raise RuntimeError(err) from e

    return signals
