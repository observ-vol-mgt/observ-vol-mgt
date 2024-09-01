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
from common.access_log import AccessLog
from common.configuration_api import InsightsAnalysisChainType

logger = logging.getLogger(__name__)


class AccessLogIntersectionAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find intersection between signals and access log entries
        """

        signals = self.get_filtered_signals()

        access_log_file_path = kwargs.get("access_log_file")
        access_log = AccessLog.from_json_file(access_log_file_path)

        not_accessed_signals = []
        not_accessed_signals_insights = "Based on analysis, the following signals are not accessed:\n"
        not_accessed_signals_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal in signals:
            if signal.metadata["__name__"] in access_log:
                continue

            signal_name = signal.metadata["__name__"]
            not_accessed_signals.append(signal_name)
            not_accessed_signals_insights += \
                (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
                 f'{signal_name}</a> - Signal is not accessed\n')
        not_accessed_signals_insights += "-=-=--=\n\n"

        self.tag_signals_by_names(not_accessed_signals,
                                  InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ACCESS_LOG_INTERSECT_NOT_ACCESSED.value)
        return self.get_signals(), not_accessed_signals_insights
