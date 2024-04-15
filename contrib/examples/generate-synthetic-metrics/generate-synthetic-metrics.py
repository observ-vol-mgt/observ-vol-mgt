import json
from datetime import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define start and end dates
start_date = '2020-01-01'
end_date = '2020-01-02'

# Create a DatetimeIndex with data points every 10 minutes
datetime_index = pd.date_range(start=start_date, end=end_date, freq='10T')

# Generate a time series with random noise
np.random.seed(0)  # for reproducibility
noise1 = np.random.normal(loc=0, scale=0.05, size=len(datetime_index))
time_series1 = pd.Series(noise1, index=datetime_index)

noise2 = np.random.normal(loc=0, scale=0.05, size=len(datetime_index))
time_series2 = pd.Series(noise2, index=datetime_index)

# Add seasonality
time_series_seasonal1 = time_series1 + np.sin(np.linspace(0, 4 * np.pi, len(time_series1))) * 0.5
time_series_seasonal2 = time_series2 + np.sin(np.linspace(0, 4 * np.pi, len(time_series2))) * 0.5

# export the data into a json formatted file
# Define the filename
output_filename = "time_series_data.json"


# Convert time series to Prometheus API

def generate_prometheus_data(time_series, metric_name):
    values_data = [[int(time_series.index[i].timestamp()), str(time_series.iloc[i])] for i in
                   range(len(time_series))]
    return [{"metric": {"__name__": metric_name}, "values": values_data}]


prometheus_data_original1 = generate_prometheus_data(time_series1, "original_time_series_metric1")
prometheus_data_seasonal1 = generate_prometheus_data(time_series_seasonal1, "seasonal_time_series_metric1")
prometheus_data_original2 = generate_prometheus_data(time_series1, "original_time_series_metric2")
prometheus_data_seasonal2 = generate_prometheus_data(time_series_seasonal1, "seasonal_time_series_metric2")

# Construct JSON structure
json_data = {
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": prometheus_data_original1 + prometheus_data_seasonal1 +
                  prometheus_data_original2 + prometheus_data_seasonal2
    }
}

# Write data to JSON file
with open(output_filename, "w") as json_file:
    json.dump(json_data, json_file, indent=4)

plot = False
if plot:
    # Plot the time series
    plt.figure(figsize=(12, 6))
    time_series1.plot(label='Original Time Series - 1')
    time_series2.plot(label='Original Time Series - 2')
    time_series_seasonal1.plot(label='Time Series - 1 with Seasonality')
    time_series_seasonal2.plot(label='Time Series - 2 with Seasonality')
    plt.title('Time Series with Seasonality')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
    # wait forever
    while True:
        # sleep one second
        time.sleep(1)
        pass
