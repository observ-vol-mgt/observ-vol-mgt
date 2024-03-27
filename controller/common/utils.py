import pandas as pd


def is_dataframe(input_data):
    return isinstance(input_data, pd.DataFrame)
