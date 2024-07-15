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

from common.signal import Signals, Signal

logger = logging.getLogger(__name__)


# Take each Signal in Signals, save its metadata, but discard the time-series data
def extract(config, signals):
    extracted_signals = Signals(metadata=signals.metadata, signals=None)

    for index, signal in enumerate(signals.signals):
        new_signal = Signal(signal.type, signal.metadata)
        extracted_signals.append(new_signal)

    return extracted_signals
