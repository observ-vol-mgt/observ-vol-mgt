import json
import logging

import numpy as np
import tsfel
import pandas as pd
from scipy.stats.stats import pearsonr

from common.signal import Signals

logger = logging.getLogger(__name__)


# ref: https://tsfel.readthedocs.io/en/latest/descriptions/get_started.html

def extract_signal(signal):
    # Normalize the time series ( to evenly sampled data in 30s granularity)
    df_signal = pd.DataFrame(signal.time_series, columns=['Time', 'value'])
    df_signal['value'] = pd.to_numeric(df_signal['value'])
    df_signal["Time"] = pd.to_datetime(df_signal["Time"], unit='s')
    df_signal = df_signal.set_index("Time")
    df_signal = df_signal.resample('30s').mean().interpolate('linear')

    # list of features to extract from configuration file
    # cfg_file = tsfel.get_features_by_domain('statistical') # ==> this will use all the statistical features
    file_path = "feature_extraction/tsfel_conf/limited_statistical.json"
    with open(file_path, 'r') as file:
        # Load the JSON data from the file
        cfg_file = json.load(file)

    # execute feature extraction
    extracted_features = tsfel.time_series_features_extractor(
        dict_features=cfg_file, signal_windows=df_signal, fs=(1 / 30), verbose=1)

    logging.debug(extracted_features.shape)
    logging.debug(extracted_features.describe())

    # append the features as labels to the signals
    signal.metadata["extracted_features"] = extracted_features

    return signal


def extract(signals):
    extracted_signals = Signals()

    # features extraction
    for index, signal in enumerate(signals):
        # extract features from the signal
        extracted_signal = extract_signal(signal)
        extracted_signals.append(extracted_signal)

    # cross-signals features extraction
    df_extracted_features = pd.DataFrame()
    for index, extracted_signal in enumerate(extracted_signals):
        extracted_signal_name = extracted_signal.metadata["__name__"]
        extracted_signal_features = extracted_signal.metadata["extracted_features"]

        # df_extracted_features.insert(index, f"{index}", extracted_signal_features.values.tolist())
        extracted_signal_features_as_column = (
            pd.DataFrame(extracted_signal_features.transpose()).rename(columns={0: extracted_signal_name}))
        df_extracted_features = pd.concat([df_extracted_features, extracted_signal_features_as_column], axis=1)

    extracted_signals.metadata["features_matrix"] = df_extracted_features

    return extracted_signals
