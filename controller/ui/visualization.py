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

import datetime
import os
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

import matplotlib.pyplot as plt
from flask import Flask, render_template, request

current_path = os.path.dirname(os.path.realpath(__file__))
flaskApp = Flask(__name__, template_folder=current_path, static_folder=f"{current_path}/static")

time_series = {}
insights = ""


def fill_time_series(extracted_signals):
    for extracted_signal in extracted_signals:
        time_series_name = extracted_signal.metadata["__name__"]
        time_series[time_series_name] = extracted_signal.time_series


def fill_insights(the_insights):
    global insights
    insights = the_insights


@flaskApp.route('/')
@flaskApp.route('/home')
@flaskApp.route('/index')
@flaskApp.route('/index.htm')
@flaskApp.route('/index.html')
def index():
    series_names = list(time_series.keys())
    return render_template('index.html', series_names=series_names)


@flaskApp.route('/insights')
def insights():
    return render_template('insights.html', insights=insights)


@flaskApp.route('/about')
def about():
    return render_template('about.html')


@flaskApp.route('/styles.css')
def serve_css():
    return flaskApp.send_static_file('styles.css')


@flaskApp.route('/signal_visualization', methods=['POST'])
def visualize():
    selected_series = request.form.getlist('timeSeries')
    plt.figure(figsize=(10, 6))

    # Plot selected time series
    all_timestamps = []
    for series_name in selected_series:
        if series_name in time_series:
            time_stamps, data = zip(*time_series[series_name])
            dates = [datetime.fromtimestamp(timestamp) for timestamp in time_stamps]
            points = [float(point) for point in data]
            plt.plot_date(x=dates, y=points, linestyle='solid', linewidth=1, label=series_name, marker='o')
        else:
            return "Error: Selected time series not found."

    # Plotting settings
    plt.title('Time Series Visualization')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))
    plt.gcf().autofmt_xdate()
    plt.xticks(rotation=45, fontsize=6)
    plt.grid(True)
    plt.legend()

    plt.savefig(f"{current_path}/static/plot.png", bbox_inches='tight')  # Save the plot as an image
    plt.close()

    return render_template('signal_visualize.html')
