import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.signal import square
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--plot", "-p", action="store_true", help="also plot the time series")
args = parser.parse_args()


# Function to convert time series to json (for Prometheus API)
def generate_prom_data(time_series, metric_name):
    values_data = [[int(time_series.index[i].timestamp()), str(time_series.iloc[i])] for i in
                   range(len(time_series))]
    return [{"metric": {"__name__": metric_name}, "values": values_data}]


# Define start and end dates
start_date = '2020-01-01'
end_date = '2020-01-02'

# Create a DatetimeIndex with data points every 10 minutes
datetime_index = pd.date_range(start=start_date, end=end_date, freq='10min')

json_metrics = []
np.random.seed(0)  # for reproducibility

# Random noise
noise1_signal = np.random.normal(loc=0, scale=0.05, size=len(datetime_index))
json_metrics += generate_prom_data(pd.Series(noise1_signal, index=datetime_index), "Noise-Zero - 1")

noise2_signal = np.random.normal(loc=0, scale=0.05, size=len(datetime_index))
json_metrics += generate_prom_data(pd.Series(noise2_signal, index=datetime_index), "Noise-Zero - 2")

# Sin
sin_signal = np.sin(np.linspace(0, 4 * np.pi, len(datetime_index))) * 0.5
json_metrics += generate_prom_data(pd.Series(sin_signal, index=datetime_index), "Sin")

# Square
square_signal = square(2 * np.pi * datetime_index.hour / 6) / 2
time_series_square_1 = pd.Series(square_signal, index=datetime_index)
json_metrics += generate_prom_data(time_series_square_1, "Square")

# Composed signals
json_metrics += generate_prom_data(pd.Series(square_signal + noise1_signal, index=datetime_index), "Square + Noise - 1")
json_metrics += generate_prom_data(pd.Series(square_signal + noise2_signal, index=datetime_index), "Square + Noise - 2")

json_metrics += generate_prom_data(pd.Series(sin_signal + noise1_signal, index=datetime_index), "Sin + Noise - 1")
json_metrics += generate_prom_data(pd.Series(sin_signal + noise2_signal, index=datetime_index), "Sin + Noise - 2")

json_metrics += generate_prom_data(pd.Series(sin_signal + square_signal, index=datetime_index), "Sin + Square")

json_metrics += generate_prom_data(pd.Series(sin_signal + square_signal + noise1_signal, index=datetime_index),
                                   "Sin + Square + Noise1")
json_metrics += generate_prom_data(pd.Series(sin_signal + square_signal + noise2_signal, index=datetime_index),
                                   "Sin + Square + Noise2")

# export the data into a json formatted file
# Define the filename
output_filename = "time_series_data.json"

# Construct JSON structure
json_data = {
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": json_metrics
    }
}

# Write data to JSON file
with open(output_filename, "w") as json_file:
    json.dump(json_data, json_file, indent=4)


if args.plot:
    # Plot the time series
    plt.figure(figsize=(12, 6))
    for json_metric in json_metrics:
        idx, val = zip(*json_metric["values"])
        time_stamps = [datetime.fromtimestamp(idx[i]) for i in range(len(idx))]
        values = [float(val[i]) for i in range(len(val))]
        pdSeries = pd.Series(values, time_stamps)
        label = json_metric["metric"]["__name__"]
        pdSeries.plot(label=label)
    plt.title('Time Series metrics')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
