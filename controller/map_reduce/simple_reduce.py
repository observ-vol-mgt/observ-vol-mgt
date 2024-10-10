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


def reduce(config, input_data):
    output_list = []
    for item in input_data:
        sublist = item[0].signals
        output_list.extend(sublist)

    # TODO: figure out what is the proper thing to do for the combined metadata
    new_signals = Signals(input_data[0][0].metadata, output_list)

    return [new_signals]
