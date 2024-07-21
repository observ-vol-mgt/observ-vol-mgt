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

import json
import logging

import pandas as pd
import tsfel

from common.signal import Signals

logger = logging.getLogger(__name__)


# ref: https://tsfel.readthedocs.io/en/latest/descriptions/get_started.html

def extract_signal(signal, features_json_file, resample_rate=30, sampling_frequency=(1/30), verbose=0):
    # Normalize the time series (to evenly sampled data in 30s granularity)
    df_signal = pd.DataFrame(signal.time_series, columns=['Time', 'value'])
    df_signal['value'] = pd.to_numeric(df_signal['value'])
    df_signal["Time"] = pd.to_datetime(df_signal["Time"], unit='s')
    df_signal = df_signal.set_index("Time")
    df_signal = df_signal.resample(resample_rate).mean().interpolate('linear')

    # list of features to extract from configuration file
    # cfg_file = tsfel.get_features_by_domain('statistical') # ==> this will use all the statistical features
    with open(features_json_file, 'r') as file:
        # Load the JSON data from the file
        cfg_file = json.load(file)

    # execute feature extraction
    extracted_features = tsfel.time_series_features_extractor(
        dict_features=cfg_file, signal_windows=df_signal, fs=sampling_frequency, verbose=verbose)

    logging.debug(extracted_features.shape)
    logging.debug(extracted_features.describe())

    # append the features as labels to the signals
    signal.metadata["extracted_features"] = extracted_features

    return signal


def extract(tsfel_config, signals):
    extracted_signals = Signals(metadata=signals.metadata)
    resample_rate = tsfel_config.resample_rate
    sampling_frequency = tsfel_config.sampling_frequency
    features_json_file = tsfel_config.features_json_file

    verbose = 1 if logging.getLogger().getEffectiveLevel() == logging.DEBUG else 0

    # features extraction
    for index, signal in enumerate(signals.signals):
        # extract features from the signal
        extracted_signal = extract_signal(
            signal, features_json_file, resample_rate, sampling_frequency, verbose)
        extracted_signals.append(extracted_signal)

    if tsfel_config.trim:
        from extract.trim_time_series import extract as extract_trim
        extracted_signals = extract_trim(None, extracted_signals)

    return extracted_signals
