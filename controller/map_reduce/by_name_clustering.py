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
import logging

logger = logging.getLogger(__name__)


def _map(config, input_data):
    logger.debug(f"map config = {config}")
    signals = input_data.signals
    clustered_signals = []
    clustered_signals_dict = {}
    name_pattern = config.name_pattern

    logger.debug(f"**************************** number of signals to map = {len(signals)}")

    if name_pattern == "" or name_pattern is None:
        return [signals]
    for signal in signals:
        match = re.search(name_pattern, signal.metadata["__name__"])
        if match:
            if match.group() not in clustered_signals_dict:
                clustered_signals_dict[match.group()] = []
            clustered_signals_dict[match.group()].append(signal)

    logger.debug(f"**************************** number of  groups = {len(clustered_signals_dict)}")

    for signal_group in clustered_signals_dict:
        logger.debug(f"**************************** signal_group = {signal_group}")
        list1 = clustered_signals_dict[signal_group]
        logger.debug(f"**************************** number of signals in group = {len(list1)}")
        new_signals = Signals(input_data.metadata, list1)
        clustered_signals.append(new_signals)

    logger.debug(f"**************************** len of  clustered_signals = {len(clustered_signals)}")
    return clustered_signals
