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

from common.signal import Signals


def extract(signals):
    extracted_signals = Signals()
    print("Not implemented")

    return extracted_signals


print("Not implemented")
exit()

# ref: https://tsfresh.readthedocs.io/en/latest/text/quick_start.html

# if the data set file doesn't exist, load from the internet
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

settings = ComprehensiveFCParameters()

X_train_sig.insert(0, 'id', '0')
print(X_train_sig.head())

X_train = extract_features(
    X_train_sig.iloc[:100], column_id="id", column_value="total_acc_x", default_fc_parameters=settings)

print(X_train.head())
print(X_train.shape)
print(X_train.describe())
print(X_train.info())
print(X_train[:1].transpose().to_markdown())
