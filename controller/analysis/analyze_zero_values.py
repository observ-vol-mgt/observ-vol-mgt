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


class ZeroValuesAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find the zero value signals
        """

        signals = self.get_filtered_signals()
        close_to_zero_threshold = kwargs.get("close_to_zero_threshold")

        zero_value_signals = []
        zero_value_insights = (f"Based on analysis, the following signals "
                               f"have close to zero values: ( up-to {close_to_zero_threshold})\n")
        zero_value_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal in signals:
            if signal.metadata["__name__"] in zero_value_signals:
                continue
            if abs(signal.metadata["extracted_features"]["value_Min"][0]) < close_to_zero_threshold and \
                    abs(signal.metadata["extracted_features"]["value_Max"][0] < close_to_zero_threshold):
                signal_name = signal.metadata["__name__"]
                zero_value_signals.append(signal_name)
                zero_value_insights += \
                    (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
                     f'{signal_name}</a> - Signal is close to zero value\n')
        zero_value_insights += "-=-=--=\n\n"

        self.tag_signals_by_names(zero_value_signals, InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value)
        return self.get_signals(), zero_value_insights
