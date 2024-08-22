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


class FixedValuesAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find signals with fixed values
        """

        signals = self.get_filtered_signals()

        fixed_value_signals = []
        fixed_value_insights = "Based on analysis, the following signals have fixed values:\n"
        fixed_value_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal in signals:
            if signal.metadata["__name__"] in fixed_value_signals:
                continue
            if ((signal.metadata["extracted_features"]["value_Min"][0] ==
                 signal.metadata["extracted_features"]["value_Max"][0]) and
                    signal.metadata["extracted_features"]["value_Var"][0] == 0):
                signal_name = signal.metadata["__name__"]
                fixed_value_signals.append(signal_name)
                fixed_value_insights += \
                    (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
                     f'{signal_name}</a> - Signal has fixed value\n')
        fixed_value_insights += "-=-=--=\n\n"

        self.tag_signals_by_names(fixed_value_signals, InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value)
        return self.get_signals(), fixed_value_insights
