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

import json
import logging
import re

from common.signal import Signal, Signals

logger = logging.getLogger(__name__)


def ingest(ingest_config):
    signals = Signals()
    ingest_file = ingest_config['file_name']
    ingest_filter_metadata = ingest_config['filter_metadata'] if 'filter_metadata' in ingest_config else None

    signals.metadata["ingest_type"] = "file"
    signals.metadata["ingest_source"] = ingest_file

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
            if ingest_filter_metadata:
                if not re.findall(ingest_filter_metadata, str(json_signal["metric"])):
                    continue
            signal_type = "metric"
            signal_metadata = json_signal["metric"]
            signal_time_series = json_signal["values"]
        else:
            raise Exception("Ingest: signal type - Not implemented")

        signals.append(Signal(type=signal_type,
                              metadata=signal_metadata,
                              time_series=signal_time_series))

    return signals
