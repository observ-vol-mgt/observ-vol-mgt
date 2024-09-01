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


class AccessLogEntry:
    def __init__(self, start, end, name, metadata={}):
        self.start = start
        self.end = end
        self.name = name
        self.metadata = metadata

    def __str__(self):
        return f"AccessLogEntry: start: {self.start}, end: {self.end}, name:{self.name}, metadata:{self.metadata}"


class AccessLog:
    def __init__(self, metadata=None):
        if metadata is None:
            metadata = {}
        self.metadata = metadata
        self.entries = []

    def append(self, entry):
        self.entries.append(entry)

    def __iter__(self):
        return iter(self.entries)

    def __contains__(self, substring):
        return any(substring in entry for entry in self.entries)

    def __getitem__(self, index):
        if isinstance(index, int):
            if 0 <= index < len(self.signals):
                return self.entries[index]
            else:
                raise IndexError("Index out of range")
        elif isinstance(index, slice):
            return [self.entries[i] for i in range(*index.indices(len(self.entries)))]
        else:
            raise TypeError("Indices must be integers or slices")

    def __str__(self):
        return f"AccessLog: entries:{self.entries}"

    @classmethod
    def from_json_file(cls, file_path):
        try:
            with open(file_path, 'r') as file:
                access_log_json_entries = json.load(file)
        except FileNotFoundError:
            raise ValueError(f"Can't load access log from file: File not found: {file_path}")

        access_log = cls(metadata={"file_path": file_path})
        for entry in access_log_json_entries:
            access_log.append(entry)
        return access_log
