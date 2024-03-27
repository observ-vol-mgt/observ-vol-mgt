import tsfel
import numpy as np
import pandas as pd
import os
import file_utils

# ref: https://tsfel.readthedocs.io/en/latest/descriptions/get_started.html

# if the data set file doesn't exist load from the internet
dataset_file = "UCI HAR Dataset.zip"
if not file_utils.file_exists(dataset_file):
    # Load the dataset from online repository
    file_utils.get_file("https://archive.ics.uci.edu/ml/machine-learning-databases/00240/UCI%20HAR%20Dataset.zip",
                        dataset_file)
    # Unzip the dataset
    file_utils.unzip_file(dataset_file)

# Store the dataset as a Pandas dataframe.
x_train_sig = np.loadtxt(
    'UCI HAR Dataset/train/Inertial Signals/total_acc_x_train.txt', dtype='float32')
X_train_sig = pd.DataFrame(np.hstack(x_train_sig), columns=["total_acc_x"])
print(X_train_sig.head())
print(X_train_sig.shape)
print(X_train_sig.describe())
print(X_train_sig.info())

# If no argument is passed retrieves all available features
cfg_file = tsfel.get_features_by_domain()
# Receives a time series sampled at 50 Hz, divides into windows of size 250 (i.e. 5 seconds) and extracts all features
X_train = tsfel.time_series_features_extractor(
    cfg_file, X_train_sig, fs=50, window_size=250)

corr_features = tsfel.correlated_features(X_train)

print(X_train.head())
print(X_train.shape)
print(X_train.describe())
print(X_train.info())
print(X_train[:1].transpose().to_markdown())
