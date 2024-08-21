

#  This is an obsolete implementation of the compound correlation analysis
#  The new implementation is in the file analyze_compound_correlations_from_raw_signals_optimized.py
#  This is kep just as a reference for the old implementation

import statsmodels.api as sm
import pandas as pd


def analyze_compound_correlations_from_raw_signals(signals):
    # todo need to optimize the creation of the data frame !!!
    # building a dataframe to represent all the signals, each as a column
    signals_dataframe = pd.DataFrame()
    for a_signal in signals.signals:
        signal_name = a_signal.metadata["__name__"]
        # signals_dataframe[signal_name] = None
        for time_point in a_signal.time_series:
            signals_dataframe.loc[pd.to_datetime(
                time_point[0], unit='s'), signal_name] = float(time_point[1])

    # analyze each of the signals (in a loop) as dependent variable (Y) and the rest as independent variables(X) for

    # debug  --> limit the signals -> signals_dataframe = signals_dataframe[["Sin", "Square", "Sin + Square",
    # "Noise-Zero - 1"]]

    insights = "We observed the following compound correlation relationships:\n\n"
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

        significant_predictors = results.pvalues[results.pvalues < 0.05].index.tolist(
        )
        if 'const' in significant_predictors:
            significant_predictors.remove('const')

        # Output significant predictors
        insights += f"The significant predictors for {signal} are: {significant_predictors}\n"

    return insights