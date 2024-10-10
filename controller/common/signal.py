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

from . import utils


class Signal:
    def __init__(self, type, metadata={}, time_series=None):
        self.type = type
        self.metadata = metadata
        self.time_series = time_series

    def set_time_series(self, time_series):
        if not utils.is_dataframe(time_series):
            raise Exception("Time series must be a pandas DataFrame")

        self.time_series = time_series

    def tag(self, tag):
        if "tags" not in self.metadata.keys():
            self.metadata["tags"] = []
        if tag not in self.metadata["tags"]:
            self.metadata["tags"].append(tag)

    def is_tagged(self, tags, _any):
        if "tags" not in self.metadata.keys():
            return False
        if _any:
            return any(tag in self.metadata["tags"] for tag in tags)
        else:
            return all(tag in self.metadata["tags"] for tag in tags)

    def __str__(self):
        return f"Signal: type: {self.type}, metadata: {self.metadata}, time_series:{self.time_series}"


class Signals:
    def __init__(self, metadata={}, signals=None):
        if signals is None:
            signals = []
        self.metadata = metadata
        self.signals = signals

    def append(self, signal):
        self.signals.append(signal)

    def filter_by_type(self, _type):
        return [signal for signal in self.signals if signal.type == _type]

    def tag_by_names(self, names, tag, filter_in=True):
        for signal in self.signals:
            if signal.metadata["__name__"] in names:
                if filter_in:
                    signal.tag(tag)
            else:
                if not filter_in:
                    signal.tag(tag)

    def filter_by_tags(self, tags, filter_in=True, _any=True):
        if filter_in:
            return [signal for signal in self.signals if signal.is_tagged(tags, _any)]
        else:
            return [signal for signal in self.signals if not signal.is_tagged(tags, _any)]

    def filter_by_names(self, names, filter_in=True):
        filtered_signals = []
        for signal in self.signals:
            if signal.metadata["__name__"] in names:
                if filter_in:
                    filtered_signals.append(signal)
            else:
                if not filter_in:
                    filtered_signals.append(signal)

        return Signals({}, filtered_signals)

    def __iter__(self):
        return iter(self.signals)

    def __getitem__(self, index):
        if isinstance(index, int):
            if 0 <= index < len(self.signals):
                return self.signals[index]
            else:
                raise IndexError("Index out of range")
        elif isinstance(index, slice):
            return [self.signals[i] for i in range(*index.indices(len(self.signals)))]
        else:
            raise TypeError("Indices must be integers or slices")

    def __str__(self):
        return f"Signal: metadata: {self.metadata}, signals:{self.signals}"
