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


class MetadataClassificationAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find the metadata classification insights
        """

        signals = self.get_filtered_signals()

        metadata_classification_insights = "Based on analysis, the metadata classification for signals:\n"
        metadata_classification_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal in signals:
            signal_name = signal.metadata["__name__"]
            if "classification" not in signal.metadata:
                continue
            signal_classification = signal.metadata["classification"]
            signal_classification_score = signal.metadata["classification_score"]
            metadata_classification_insights += \
                (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
                 f'{signal_name}</a> - Signal is '
                 f'classified as {signal_classification} '
                 f'with a score of {signal_classification_score}\n')
        metadata_classification_insights += "-=-=--=\n\n"

        self.tag_signals_by_names(signals, InsightsAnalysisChainType.INSIGHTS_ANALYSIS_METADATA_CLASSIFICATION.value)
        return self.get_signals(), metadata_classification_insights
