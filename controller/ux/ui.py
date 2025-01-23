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

import logging
import os
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from datetime import datetime

import matplotlib.pyplot as plt
from flask import render_template, request, Blueprint
from ux.utils import get_insights, get_time_series

logger = logging.getLogger(__name__)

current_path = os.path.dirname(os.path.realpath(__file__))
ui = Blueprint('visualization', __name__,
               template_folder=current_path,
               static_folder=f"{current_path}/static")


@ui.route('/')
@ui.route('/home')
@ui.route('/index')
@ui.route('/index.htm')
@ui.route('/index.html')
def _index():
    series_names = list(get_time_series().keys())
    return render_template('index.html', series_names=series_names)


@ui.route('/insights')
def _insights():
    return render_template('insights.html', insights=get_insights())


@ui.route('/about')
def _about():
    return render_template('about.html')


@ui.route('/styles.css')
def _serve_css():
    return ui.send_static_file('styles.css')


@ui.route('/signal_visualization', methods=['POST'])
def _visualize():
    selected_series = request.form.getlist('timeSeries')
    plt.figure(figsize=(10, 6))

    # Plot selected time series
    for series_name in selected_series:
        if series_name in get_time_series():
            time_stamps, data = zip(*get_time_series()[series_name])
            dates = [datetime.fromtimestamp(timestamp)
                     for timestamp in time_stamps]
            points = [float(point) for point in data]
            plt.plot_date(x=dates, y=points, linestyle='solid',
                          linewidth=1, label=series_name, marker='o')
        else:
            return "Error: Selected time series not found."

    # Plotting settings
    plt.title('Time Series Visualization')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))
    plt.gcf().autofmt_xdate()
    plt.xticks(rotation=45, fontsize=6)
    plt.grid(True)
    plt.legend()

    plt.savefig(f"{current_path}/static/plot.png",
                bbox_inches='tight')  # Save the plot as an image
    plt.close()

    return render_template('signal_visualize.html')
