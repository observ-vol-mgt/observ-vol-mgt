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
from abc import ABC
from analysis.analyzer import Analyzer
from common.configuration_api import InsightsAnalysisChainType

logger = logging.getLogger(__name__)


class MonotonicAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find signals which are monotonic
        """

        signals = self.get_filtered_signals()

        monotonic_signals = []
        monotonic_insights = "Based on analysis, the following signals are monotonic:\n"
        monotonic_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal in signals:
            if signal.metadata["__name__"] in monotonic_signals:
                continue
            if self.monotonic_inc(signal) or self.monotonic_dec(signal):
                signal_name = signal.metadata["__name__"]
                monotonic_signals.append(signal_name)
                monotonic_insights += \
                    (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
                     f'{signal_name}</a> - Signal is monotonic\n')
        monotonic_insights += "-=-=--=\n\n"

        self.tag_signals_by_names(monotonic_signals, InsightsAnalysisChainType.INSIGHTS_ANALYSIS_MONOTONIC.value)
        return self.get_signals(), monotonic_insights

    def monotonic_inc(self, signal):
        # assuming the time series is in order
        for k in range(len(signal.time_series)-1):
            if signal.time_series[k][1] < signal.time_series[k+1][1]:
                return False
        return True

    def monotonic_dec(self, signal):
        # assuming the time series is in order
        for k in range(len(signal.time_series)-1):
            if signal.time_series[k][1] > signal.time_series[k+1][1]:
                return False
        return True
