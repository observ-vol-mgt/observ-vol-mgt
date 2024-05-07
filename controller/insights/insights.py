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
import statsmodels.api as sm
import statsmodels.stats.outliers_influence as oi

logger = logging.getLogger(__name__)


def generate_insights(stage, signals_list):
    signals = signals_list[0]
    # Get the pairwise correlation between signals
    pairwise_signals_to_keep, pairwise_signals_to_reduce, pairwise_correlation_insights = (
        analyze_correlations(signals))

    # Get the composed correlation for the remaining signals
    signals_to_keep_post_pairwise_correlation = signals.filter_by_names(pairwise_signals_to_keep)
    composed_signals_to_keep, composed_signals_to_reduce, composed_correlation_insights = (
        analyze_composed_correlations(signals_to_keep_post_pairwise_correlation))

    summary_insights = f"\n ==> Summary: The signals to keep are: {composed_signals_to_keep}:\n\n"
    return (composed_signals_to_keep,
            [signal["signal"] for signal in pairwise_signals_to_reduce] +
            [signal["signal"] for signal in composed_signals_to_reduce],
            pairwise_correlation_insights + composed_correlation_insights + summary_insights)


def analyze_correlations(signals):
    """
    Find the pairwise correlation between signals
    """

    # Execute cross signal correlation
    threshold = 0.95
    features_matrix = signals.metadata["features_matrix"]
    corr_matrix = features_matrix.corr(method='pearson')
    signals.metadata["corr_matrix"] = corr_matrix

    # label each of the signals with the correlation with all other signals
    for index, extracted_signal in enumerate(signals):
        extracted_signal_name = extracted_signal.metadata["__name__"]
        extracted_signal.metadata["corr_features"] = corr_matrix[extracted_signal_name]

    # Analyze the list of signals that can be reduces

    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    # Find index and column name of features with high correlation
    signals_to_reduce = []
    signals_to_keep = []
    for column in upper.columns:
        keep_metric = True
        for index in upper.index:
            if upper.loc[index, column] > threshold:
                signals_to_reduce.append({"signal": column, "correlated_signals": index})
                keep_metric = False
                break
        if keep_metric:
            signals_to_keep.append(column)

    # Generate the insights
    insights = f"Based on pairwise correlation analysis we can reduce:\n"
    insights += f"-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
    for signal_to_reduce in signals_to_reduce:
        signal = signal_to_reduce["signal"]
        correlated_signals = signal_to_reduce["correlated_signals"]
        insights += f"{signal} - it is highly correlated with {correlated_signals}\n"
    insights += f"-=-=--=\n\n"

    logging.debug(f"\n\n{insights}\n")
    return signals_to_keep, signals_to_reduce, insights


def analyze_composed_correlations(signals):
    # This method is using the original raw signals, this is not really working well,
    # and it requires significant computational resources. We will use the features,
    # version of the analysis and not use the function `analyze_composed_correlations_from_raw_signals`
    # insights=analyze_composed_correlations_from_raw_signals(signals)
    # return insights

    # will hold the signals we need to keep based on the analysis
    signals_to_keep = []

    # this is an opinionated list of selected features used to commute the linear correlation between
    # multiple independent signals and the dependent signal
    selected_features = ["value_Min", "value_Max", "value_Mean", "value_Var", "value_PeakToPeakDistance", "value_AbsoluteEnergy"]

    signals_features_matrix = pd.DataFrame()
    for signal in signals.signals:
        signals_features_matrix[signal.metadata["__name__"]] = (
            signal.metadata["extracted_features"][selected_features].transpose())

    dependent_signals = {}
    for the_signal in signals_features_matrix.columns:
        features_matrix_to_test = signals_features_matrix.drop(columns=[the_signal])
        features_matrix_to_test = sm.add_constant(features_matrix_to_test)
        model = sm.OLS(signals_features_matrix[the_signal], features_matrix_to_test)
        results = model.fit()
        logger.info(results.summary())
        significant_signal_predictors = results.pvalues[results.pvalues < 0.01].index.tolist()
        if 'const' in significant_signal_predictors:
            significant_signal_predictors.remove('const')
        if significant_signal_predictors:
            # Print significant predictors
            logger.debug(f"The significant predictors for {the_signal} are: {significant_signal_predictors}")
            dependent_signals[the_signal] = significant_signal_predictors
        else:
            signals_to_keep += [the_signal]
            logger.debug(f"The significant predictors for {the_signal} are: None")

    insights = f"Based on composed correlation relationship predictions we can also reduce:\n"
    insights += f"-=-=--=-=-=--=-=-=--=-=-=--=-=-=--=\n"
    signals_to_reduce = []
    for the_signal in dependent_signals:
        # skip signals that are used to predict other signals
        if the_signal in signals_to_keep:
            continue
        insights += f"{the_signal} - it is constructed from {dependent_signals[the_signal]}\n"
        signals_to_reduce.append({"signal": the_signal, "constructed_from": dependent_signals[the_signal]})
        signals_to_keep += dependent_signals[the_signal]
    insights += f"-=-=--=\n\n"

    logging.debug(f"\n\n{insights}\n")
    return signals_to_keep, signals_to_reduce, insights


def analyze_composed_correlations_from_raw_signals(signals):
    # todo need to optimize the creation of the data frame !!!
    # building a dataframe to represent all the signals, each as a column
    signals_dataframe = pd.DataFrame()
    for a_signal in signals.signals:
        signal_name = a_signal.metadata["__name__"]
        # signals_dataframe[signal_name] = None
        for time_point in a_signal.time_series:
            signals_dataframe.loc[pd.to_datetime(time_point[0], unit='s'), signal_name] = float(time_point[1])

    # analyze each of the signals (in a loop) as dependent variable (Y) and the rest as independent variables(X) for

    # debug  --> limit the signals -> signals_dataframe = signals_dataframe[["Sin", "Square", "Sin + Square",
    # "Noise-Zero - 1"]]

    insights = f"We observed the following composed correlation relationships:\n\n"
    for signal in signals_dataframe.columns:
        signals_matrix_test = signals_dataframe.drop(columns=[signal])
        signals_matrix_test = sm.add_constant(signals_matrix_test)

        # Calculate VIF for each independent variable
        vif = pd.DataFrame()
        vif["Features"] = signals_matrix_test.columns
        vif["VIF"] = [oi.variance_inflation_factor(signals_matrix_test.values, i) for i in
                      range(signals_matrix_test.shape[1])]
        print("VIF for", signal)
        print(vif)

        model = sm.OLS(signals_dataframe[signal], signals_matrix_test)
        results = model.fit()
        print(results.summary())

        significant_predictors = results.pvalues[results.pvalues < 0.05].index.tolist()
        if 'const' in significant_predictors:
            significant_predictors.remove('const')

        # Output significant predictors
        insights += f"The significant predictors for {signal} are: {significant_predictors}\n"

    return insights
