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

import pandas as pd


def is_dataframe(input_data):
    return isinstance(input_data, pd.DataFrame)


def remove_dictionary_keys(dictionary, keys_to_remove):
    for key in list(dictionary.keys()):
        if key in keys_to_remove:
            del dictionary[key]


def add_slash_to_dir(directory):
    if directory and not directory.endswith('/'):
        directory += '/'
    return directory
