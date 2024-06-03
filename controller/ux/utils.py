#   Copyright 2024 IBM, Inc.
#  #
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  #
#       http://www.apache.org/licenses/LICENSE-2.0
#  #
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

logger = logging.getLogger(__name__)

time_series = {}
the_insights = ""


def fill_time_series(extracted_signals):
    global time_series
    time_series = {}
    for extracted_signal in extracted_signals:
        time_series_name = extracted_signal.metadata["__name__"]
        time_series[time_series_name] = extracted_signal.time_series


def get_time_series():
    global time_series
    return time_series


def fill_insights(_insights):
    global the_insights
    the_insights = _insights


def get_insights():
    global the_insights
    return the_insights
