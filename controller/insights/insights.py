import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.outliers_influence as oi

logger = logging.getLogger(__name__)


def generate_insights(signals):
    causality_insights = analyze_composed_correlations(signals)
    correlation_insights = analyze_correlations(signals)
    return correlation_insights + causality_insights


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
        vif["VIF"] = [oi.variance_inflation_factor(signals_matrix_test.values, i) for i in range(signals_matrix_test.shape[1])]
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


def analyze_composed_correlations(signals):

    # This method is using the original raw signals, this is not really working well,
    # and it requires significant computational resources. We will try to use the features,
    # version of the analysis and not use the function `analyze_composed_correlations_from_raw_signals`

    # insights=analyze_composed_correlations_from_raw_signals(signals)
    # return insights

    insights = f"We observed the following composed correlation relationships:\n\n"
    features_matrix = signals.metadata["features_matrix"]
    for feature in features_matrix.columns:
        features_matrix_test = features_matrix.drop(columns=[feature])
        features_matrix_test = sm.add_constant(features_matrix_test)
        model = sm.OLS(features_matrix[feature], features_matrix_test)
        results = model.fit()
        significant_predictors = results.pvalues[results.pvalues < 0.05].index.tolist()
        if 'const' in significant_predictors:
            significant_predictors.remove('const')

        # Print significant predictors
        insights += f"The significant predictors for {feature} are: {significant_predictors}\n"

    insights += f"-=-=--=\n\n"
    return insights


def analyze_correlations(signals):
    """
    Find the correlation between signals
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
    metrics_to_reduce = []
    for column in upper.columns:
        for index in upper.index:
            if upper.loc[index, column] > threshold:
                metrics_to_reduce.append({"metric": column, "correlated_metric": index})
                break

    # Generate the insights
    insights = f"Based on pairwise correlation analysis we can reduce:\n\n"
    for metric_to_reduce in metrics_to_reduce:
        metric = metric_to_reduce["metric"]
        correlated_metric = metric_to_reduce["correlated_metric"]
        insights += f"{metric} - it is highly correlated with {correlated_metric}\n"
    insights += f"-=-=--=\n\n"

    logging.debug(f"\n\n{insights}\n")

    return insights
