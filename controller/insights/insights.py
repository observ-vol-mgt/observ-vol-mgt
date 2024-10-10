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
import common.configuration_api as api
from analysis.analyze_compound_correlations import CompoundCorrelationAnalyzer
from analysis.analyze_fixed_values import FixedValuesAnalyzer
from analysis.analyze_intersect_with_access_log import AccessLogIntersectionAnalyzer
from analysis.analyze_metadata_classification import MetadataClassificationAnalyzer
from analysis.analyze_pairwise_correlations import PairwiseCorrelationAnalyzer
from analysis.analyze_zero_values import ZeroValuesAnalyzer

logger = logging.getLogger(__name__)


def generate_insights(subtype, config, input_data):
    if len(input_data) != 1:
        raise "generate_insights configuration should have one input"
    signals = input_data[0]
    # verify config parameters conform to structure
    typed_config = api.GenerateInsights(**config)

    # Get the chain of analysis processes to execute
    analysis_chain = typed_config.analysis_chain

    # execute the analysis according to the chain
    insights = []
    for analysis_process in analysis_chain:
        logger.info(f"Performing analysis process {analysis_process}")

        if analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES:
            # finding zero signals
            zero_values_analyzer = ZeroValuesAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags
            close_to_zero_threshold = analysis_process.close_to_zero_threshold

            zero_values_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                zero_values_analyzer.analyze(close_to_zero_threshold=close_to_zero_threshold))
            insights.append(result_insights)

        elif analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_FIXED_VALUES:
            # finding fixed signals
            fixed_values_analyzer = FixedValuesAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags

            fixed_values_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                fixed_values_analyzer.analyze())
            insights.append(result_insights)

        elif analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS:
            # finding pairwise correlated signals
            pairwise_correlation_analyzer = PairwiseCorrelationAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags
            pairwise_similarity_threshold = analysis_process.pairwise_similarity_threshold
            pairwise_similarity_method = analysis_process.pairwise_similarity_method
            pairwise_similarity_distance_method = analysis_process.pairwise_similarity_distance_method

            pairwise_correlation_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                pairwise_correlation_analyzer.analyze(
                    pairwise_similarity_threshold=pairwise_similarity_threshold,
                    pairwise_similarity_method=pairwise_similarity_method,
                    pairwise_similarity_distance_method=pairwise_similarity_distance_method))
            insights.append(result_insights)

        elif analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_COMPOUND_CORRELATIONS:
            # finding pairwise correlated signals
            compound_correlation_analyzer = CompoundCorrelationAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags
            compound_similarity_threshold = analysis_process.compound_similarity_threshold

            compound_correlation_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                compound_correlation_analyzer.analyze(compound_similarity_threshold=compound_similarity_threshold))
            insights.append(result_insights)
        elif analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_METADATA_CLASSIFICATION:
            # finding pairwise correlated signals
            metadata_classification_analyzer = MetadataClassificationAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags

            metadata_classification_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                metadata_classification_analyzer.analyze())
            insights.append(result_insights)
        elif analysis_process.type == api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ACCESS_LOG_INTERSECT:
            # finding intersection with access_log
            access_log_intersection_analyzer = AccessLogIntersectionAnalyzer(signals)

            filter_signals_by_tags = analysis_process.filter_signals_by_tags
            access_log_file = analysis_process.access_log_file

            access_log_intersection_analyzer.filter_signals_by_tags(filter_signals_by_tags, out=True, _any=True)
            signals, result_insights = (
                access_log_intersection_analyzer.analyze(access_log_file=access_log_file))
            insights.append(result_insights)
        else:
            raise "unsupported analysis process"

    # Get summary insights
    reduce_signals_tags = [api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_ZERO_VALUES.value,
                           api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_FIXED_VALUES.value,
                           api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_PAIRWISE_CORRELATIONS.value,
                           api.InsightsAnalysisChainType.INSIGHTS_ANALYSIS_COMPOUND_CORRELATIONS.value]
    signals_to_reduce = signals.filter_by_tags(reduce_signals_tags, filter_in=True, _any=True)
    signals_to_keep = signals.filter_by_tags(reduce_signals_tags, filter_in=False, _any=True)

    result_insights = insights_summary(signals_to_keep)
    insights.append(result_insights)

    return [[signal.metadata["__name__"] for signal in signals_to_keep],
            [signal.metadata["__name__"] for signal in signals_to_reduce],
            insights]


def insights_summary(signals):
    summary_insights = "Based on analysis, summary, signals to keep:\n"
    summary_insights += "-=-=--=-=-=--=-=-==-=-=--==--==--==--==--=-\n"
    for signal in signals:
        signal_name = signal.metadata["__name__"]
        summary_insights += \
            (f'<a href="javascript:void(0);" onclick="submitForm(&apos;{signal_name}&apos;);">'
             f'{signal_name}</a>\n')
    summary_insights += "-=-=--=\n\n"
    return summary_insights
