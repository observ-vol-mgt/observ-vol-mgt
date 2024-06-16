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

import re
from common.signal import Signals


def _map(config, signals):
    clustered_signals = []
    clustered_signals_dict = {}
    name_pattern = config.name_pattern

    if name_pattern == "" or name_pattern is None:
        return [signals]

    for signal in signals:
        match = re.search(name_pattern, signal.metadata["__name__"])
        if match:
            if match.group() not in clustered_signals_dict:
                clustered_signals_dict[match.group()] = []
            clustered_signals_dict[match.group()].append(signal)

    clustered_signals = list(clustered_signals_dict.values())
    clustered_signals_list = []
    for clustered_signals_group in clustered_signals:
        clustered_signals_list.append(Signals(signals.metadata, clustered_signals_group))

    return clustered_signals_list
