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
from abc import ABC, abstractmethod
from common.signal import Signals

logger = logging.getLogger(__name__)


class Analyzer(ABC):
    def __init__(self, signals):
        self.signals = signals
        self.filtered_signals = signals

    @abstractmethod
    def analyze(self, *args, **kwargs):
        pass

    def get_filtered_signals(self):
        return self.filtered_signals

    def get_signals(self):
        return self.signals

    def filter_signals_by_tags(self, tags, out=False, _any=False):
        if out:
            filtered_signals = [signal for signal in self.signals if not signal.is_tagged(tags, _any)]
            self.filtered_signals = Signals(metadata=self.signals.metadata, signals=filtered_signals)
        else:
            filtered_signals = [signal for signal in self.signals if not signal.is_tagged(tags, _any)]
            self.filtered_signals = Signals(metadata=self.signals.metadata, signals=filtered_signals)

    def tag_signals_by_names(self, names, tag):
        for signal in self.signals:
            if signal.metadata["__name__"] in names:
                signal.tag(tag)
