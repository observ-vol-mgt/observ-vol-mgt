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

from common.signal import Signal, Signals


def ingest():
    signals = Signals()

    signals.metadata["ingest_type"] = "dummy"
    signals.metadata["ingest_source"] = "dummy_source"

    signals.append(Signal(type="metric", time_series={
                   'time': [1, 2, 3], 'values': [10, 20, 30]}))

    return signals
