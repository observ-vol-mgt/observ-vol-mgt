from common.signal import Signal, Signals
from common.conf import get_configuration
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime


def ingest():
    signals = Signals()
    signal_type = "metric"

    ingest_url = get_configuration()["ingest_url"]
    ingest_window = get_configuration()["ingest_window"]

    signals.metadata["ingest_type"] = "promql"
    signals.metadata["ingest_source"] = ingest_url
    signals.metadata["ingest_window"] = ingest_window

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
