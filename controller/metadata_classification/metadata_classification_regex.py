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

from common.signal import Signals

logger = logging.getLogger(__name__)


def metadata_classification(config, signals):
    classified_signals = Signals(metadata=signals.metadata, signals=[])

    regex_file = config.regex_classification_file

    # Loading regexes for classification
    with open(regex_file) as f:
        regex_dict = json.load(f)

    # metadata classification for signals
    for signal in signals:
        # extract features from the signal
        classification_result = metadata_classification_signal(regex_dict, signal)
        classified_signal = signal
        classified_signal.metadata['classification'] = classification_result['labels'][0]
        classified_signal.metadata['classification_score'] = classification_result['scores'][0]
        classified_signals.signals.append(classified_signal)

    return classified_signals


def metadata_classification_signal(regex_dict, signal):
    metadata = f"{signal.metadata}"
    logger.debug(f"Metadata for classify: {metadata}")
    for count, (label, regex_pattern) in enumerate(regex_dict.items()):
        match = re.compile(regex_pattern).search(metadata)
        if match:
            return {'labels': [label], 'scores': [1.0]}
            break

    return {'labels': ['unknown'], 'scores': [0.0]}
