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

import pandas as pd
import statsmodels.api as sm
from abc import ABC
from analysis.analyzer import Analyzer
from common.configuration_api import InsightsAnalysisChainType

logger = logging.getLogger(__name__)


class CompoundCorrelationAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        # This method is using the original raw signals, this is not really working well,
        # and it requires significant computational resources. We will use the features,
        # version of the analysis and not use the function `analyze_compound_correlations_from_raw_signals`
        # insights=analyze_compound_correlations_from_raw_signals(signals)
        # return insights

        signals = self.get_filtered_signals()
        compound_similarity_threshold = kwargs.get("compound_similarity_threshold")

        # will hold the signals we need to keep based on the analysis
        signals_to_keep = []

        # this is an opinionated list of selected features used to commute the linear correlation between
        # multiple independent signals and the dependent signal
        selected_features = ["value_Min", "value_Max", "value_Mean", "value_Var", "value_PeakToPeakDistance",
                             "value_AbsoluteEnergy"]

        signals_features_matrix = pd.DataFrame()
        for signal in signals.signals:
            signals_features_matrix[signal.metadata["__name__"]] = (
                signal.metadata["extracted_features"][selected_features].transpose())

        threshold = 1.0 - compound_similarity_threshold
        dependent_signals = {}
        for the_signal in signals_features_matrix.columns:
            features_matrix_to_test = signals_features_matrix.drop(columns=[
                the_signal])
            features_matrix_to_test = sm.add_constant(features_matrix_to_test)
            model = sm.OLS(
                signals_features_matrix[the_signal], features_matrix_to_test)
            results = model.fit()
            logger.debug(results.summary())
            significant_signal_predictors = results.pvalues[results.pvalues < threshold].index.tolist(
            )
            if 'const' in significant_signal_predictors:
                significant_signal_predictors.remove('const')
            if significant_signal_predictors:
                # Print significant predictors
                logger.debug(
                    f"The significant predictors for {the_signal} are: {significant_signal_predictors}")
                dependent_signals[the_signal] = significant_signal_predictors
            else:
                signals_to_keep += [the_signal]
                logger.debug(
                    f"The significant predictors for {the_signal} are: None")

        compound_insights = "Based on compound correlation relationship predictions we can also reduce:\n"
        compound_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        signals_to_reduce = []
        for the_signal in dependent_signals:
            # skip signals that are used to predict other signals
            if the_signal in signals_to_keep:
                continue

            compound_insights += \
                (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{the_signal}&apos;);">'
                 f'{the_signal}</a> - it is constructed from '
                 f'{dependent_signals[the_signal]}\n\n')

            signals_to_reduce.append(
                {"signal": the_signal, "constructed_from": dependent_signals[the_signal]})
            signals_to_keep += dependent_signals[the_signal]
        compound_insights += "-=-=--=\n\n"

        logging.debug(f"\n\n{compound_insights}\n")
        self.tag_signals_by_names([signal["signal"] for signal in signals_to_reduce],
                                  InsightsAnalysisChainType.INSIGHTS_ANALYSIS_COMPOUND_CORRELATIONS.value)
        return self.get_signals(), compound_insights
