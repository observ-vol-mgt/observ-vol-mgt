#  Copyright 2024 IBM, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import re
from string import Template
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

from common.configuration_api import IngestSubType
from common.signal import Signal, Signals

logger = logging.getLogger(__name__)


def ingest(ingest_config):
    ingest_url = ingest_config.url
    ingest_window = ingest_config.ingest_window
    ingest_name_template = ingest_config.ingest_name_template
    ingest_filter_metadata = ingest_config.filter_metadata

    signals = Signals()
    signal_type = "metric"

    signals.metadata["ingest_type"] = IngestSubType.PIPELINE_INGEST_PROMQL.value
    signals.metadata["ingest_source"] = ingest_url
    signals.metadata["ingest_window"] = ingest_window

    try:
        prom = PrometheusConnect(url=ingest_url, disable_ssl=True)
        metrics = prom.all_metrics()
        signal_count = 0
        for metric in metrics:
            start_time = parse_datetime(ingest_window)
            end_time = parse_datetime("now")
            metric_data = prom.get_metric_range_data(
                metric,
                start_time=start_time,
                end_time=end_time,
            )
            for signal in metric_data:
                if ingest_filter_metadata != "":
                    if not re.findall(ingest_filter_metadata, str(signal["metric"])):
                        continue
                if ingest_name_template != "":
                    # adding `count` to allow usage by template
                    signal["metric"]["count"] = signal_count
                    # save original signal name into `original_name` if needed
                    if "__name__" in signal["metric"]:
                        signal["metric"]["original_name"] = signal["metric"]["__name__"]
                    # build new name based on template
                    signal["metric"]["__name__"] = Template(
                        ingest_name_template).safe_substitute(signal["metric"])

                signals.append(Signal(
                    type=signal_type, metadata=signal['metric'], time_series=signal['values']))
                signal_count += 1

    except Exception as e:
        err = f"The url {ingest_url} does not exist {e}"
        raise RuntimeError(err) from e

    logger.info(f"Ingested {len(signals.signals)} signals from {ingest_url} ")
    return signals
