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

import numpy as np
import pandas as pd
import common.configuration_api as api
from scipy.spatial.distance import pdist, squareform
from abc import ABC
from analysis.analyzer import Analyzer
from common.configuration_api import InsightsAnalysisChainType

logger = logging.getLogger(__name__)


class PairwiseCorrelationAnalyzer(Analyzer, ABC):

    def analyze(self, *args, **kwargs):
        """
        Find the pairwise correlation between signals
        """

        signals = self.get_filtered_signals()
        pairwise_similarity_threshold = kwargs.get("pairwise_similarity_threshold")
        pairwise_similarity_method = kwargs.get("pairwise_similarity_method")
        pairwise_similarity_distance_method = kwargs.get("pairwise_similarity_distance_method")

        if not signals.signals:
            return self.get_signals(), "No insights, empty signals"

        # cross-signals features extraction
        df_features_matrix = pd.DataFrame()
        for index, signal in enumerate(signals):
            signal_name = signal.metadata["__name__"]
            signal_features = signal.metadata["extracted_features"]

            extracted_signal_features_as_column = (
                pd.DataFrame(signal_features.transpose()).rename(columns={0: signal_name}))
            df_features_matrix = pd.concat(
                [df_features_matrix, extracted_signal_features_as_column], axis=1)

        # Execute cross signal correlation

        # using pdist distance function
        if pairwise_similarity_method == api.GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_DISTANCE.value:
            df_transposed = df_features_matrix.T
            dist_matrix = pdist(df_transposed, metric=pairwise_similarity_distance_method)
            dist_matrix_square = squareform(dist_matrix)
            corr_matrix = pd.DataFrame(dist_matrix_square,
                                       index=df_transposed.index,
                                       columns=df_transposed.index)
        else:
            # using Pandas corr function with method
            corr_matrix = df_features_matrix.corr(method=pairwise_similarity_method)

        signals.metadata["corr_matrix"] = corr_matrix

        # label each of the signals with the correlation with all other signals
        for index, extracted_signal in enumerate(signals):
            extracted_signal_name = extracted_signal.metadata["__name__"]
            extracted_signal.metadata["corr_signals"] = corr_matrix[extracted_signal_name]

        # Analyze the list of signals that can be reduces

        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

        # Find index and column name of features with high correlation
        signals_to_reduce = []
        signals_to_keep = []
        for column in upper.columns:
            keep_metric = True
            for index in upper.index:
                if pairwise_similarity_method == api.GenerateInsightsType.INSIGHTS_SIMILARITY_METHOD_DISTANCE.value:
                    if upper.loc[index, column] <= pairwise_similarity_threshold:
                        signals_to_reduce.append(
                            {"signal": column, "correlated_signals": index})
                        keep_metric = False
                        break
                else:
                    if upper.loc[index, column] > pairwise_similarity_threshold:
                        signals_to_reduce.append(
                            {"signal": column, "correlated_signals": index})
                        keep_metric = False
                        break
            if keep_metric:
                signals_to_keep.append(column)

        # Generate the insights
        pairwise_insights = "Based on pairwise correlation analysis we can reduce:\n"
        pairwise_insights += "-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
        for signal_to_reduce in signals_to_reduce:
            signal = signal_to_reduce["signal"]
            correlated_signals = signal_to_reduce["correlated_signals"]
            pairwise_insights += \
                (f'<a href="javascript:void(0);" '
                 f'onclick="submitForm(&apos;{signal}&apos;);">'
                 f'{signal}</a> - it is highly correlated with '
                 f'<a href="javascript:void(0);" '
                 f'onclick="submitForm([&apos;{signal}&apos;, &apos;{correlated_signals}&apos;]);">'
                 f'{correlated_signals}</a>'
                 f'\n\n')
        pairwise_insights += "-=-=--=\n\n"

        logging.debug(f"\n\n{pairwise_insights}\n")
        self.tag_signals_by_names([signal["signal"] for signal in signals_to_reduce],
                                  InsightsAnalysisChainType.INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS.value)
        return self.get_signals(), pairwise_insights
