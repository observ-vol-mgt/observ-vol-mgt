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

from common.signal import Signals


def _map(config, input_data):
    number_of_lists = config.number
    if number_of_lists <= 0:
        raise "illegal number of output lists for split"
    signals = input_data.signals
    n_records = len(signals)
    list_size = n_records // number_of_lists
    list_of_outputs = []
    for index in range(number_of_lists-1):
        start = index * list_size
        end = (index+1) * list_size
        list1 = [signals[j] for j in range(start, end)]
        new_signals = Signals(input_data.metadata, list1)
        list_of_outputs.append(new_signals)
    start = (number_of_lists-1) * list_size
    end = n_records
    list1 = [input_data[j] for j in range(start, end)]
    new_signals = Signals(input_data.metadata, list1)
    list_of_outputs.append(new_signals)
    return list_of_outputs
