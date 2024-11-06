#   Copyright 2024 IBM, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import os
import re

import requests
import json
import argparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def fetch_instana_plugins_catalog(url, token, plugins_filter):
    # Instana API endpoint for fetching plugins
    instana_api_url = f"{url}/api/infrastructure-monitoring/catalog/plugins"

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    # Make a GET request to fetch plugins
    response = requests.get(instana_api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        plugins = list(map(lambda item: item['plugin'], response.json()))
        if plugins_filter:
            plugins_filter_regex = re.compile(plugins_filter)
            plugins = [plugin for plugin in plugins if plugins_filter_regex.search(plugin)]
        return plugins
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


def fetch_instana_snapshot_details(url, token, snapshot_id):
    # Instana API endpoint for fetching plugins
    instana_api_url = f"{url}/api/infrastructure-monitoring/snapshots/{snapshot_id}"

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    # Make a GET request to fetch plugins
    response = requests.get(instana_api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


def fetch_instana_snapshots(url, token, plugin, start_time, end_time, query):
    # Instana API endpoint for fetching plugins
    instana_api_url = f"{url}/api/infrastructure-monitoring/snapshots"

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    params = {
        "start": int(start_time.timestamp()) * 1000,  # Convert to milliseconds
        "end": int(end_time.timestamp()) * 1000,  # Convert to milliseconds
    }

    parameters = {'plugin': plugin,
                  'to': params["end"],
                  'query': query,
                  'windowSize': params["end"] - params["start"]}

    # fetch metrics
    response = requests.get(instana_api_url, params=parameters, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return list(map(lambda item: item['snapshotId'], response.json()['items']))
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


def fetch_instana_metrics_catalog(url, token, plugin):
    # Instana API endpoint for fetching plugins
    instana_api_url = f"{url}/api/infrastructure-monitoring/catalog/metrics/{plugin}"

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    # fetch catalog of metrics
    response = requests.get(instana_api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


# fetch metrics from Instana API
def fetch_instana_infrastructure_metrics(url, token, plugin, snapshots, metric_ids, start_time, end_time, rollup):
    # Instana API endpoint for fetching metrics
    instana_api_url = f"{url}/api/infrastructure-monitoring/metrics"

    # Define params
    params = {
        "start": int(start_time.timestamp()) * 1000,  # Convert to milliseconds
        "end": int(end_time.timestamp()) * 1000,  # Convert to milliseconds
    }

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    body = {
        "query": "",
        "metrics": metric_ids,
        "snapshotIds": snapshots,
        "plugin": plugin,
        'rollup': rollup,
        "timeFrame": {"to": params["end"],
                      "windowSize": params["end"] - params["start"]}
    }
    parameters = {'offline': True}

    # fetch metrics
    response = requests.post(instana_api_url, params=parameters, headers=headers, json=body)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching metrics:", response.text)
        return None


def fetch_instana_metrics(url, token, start_time, end_time, rollup, snapshots_query, plugins_filter, limit=1000):
    time_series_metrics = []
    metrics_count = 0
    plugins = fetch_instana_plugins_catalog(url, token, plugins_filter)
    if plugins is None:
        return None

    # for each plugin, fetch snapshots and metrics
    for p in range(0, len(plugins)):
        plugin = plugins[p]
        logging.info(f"fetching metrics for plugin: {plugin} [{p}/{len(plugins)}]")

        # fetch the snapshots
        snapshots = fetch_instana_snapshots(url, token, plugin, start_time, end_time, snapshots_query)
        if not snapshots:
            continue

        # fetch the metric ids
        metrics_catalog = fetch_instana_metrics_catalog(url, token, plugin)
        if metrics_catalog is None:
            continue
        metric_ids = list(map(lambda item: item['metricId'], metrics_catalog))

        # fetch the time_series metrics
        metrics_api_limit = 5  # <<<--- limitation of the API to max 5 metrics per call
        snapshots_api_limit = 30  # <<<--- limitation of the API to max 30 snapshots per call
        for i in range(0, len(snapshots), snapshots_api_limit):
            snapshots_subset = snapshots[i:i + snapshots_api_limit]

            if logging.getLogger().isEnabledFor(logging.DEBUG):
                for snapshot_id in snapshots_subset:
                    snapshot_details = fetch_instana_snapshot_details(url, token, snapshot_id)
                    logging.debug(f"For snapshot {snapshot_id} details are: {snapshot_details}")

            for j in range(0, len(metric_ids), metrics_api_limit):
                metric_ids_subset = metric_ids[j:j + metrics_api_limit]
                logging.info(f"=> fetching time series for plugin: {plugin}, "
                             f"snapshots: [{i}.. /{len(snapshots)}] "
                             f"metrics: [{j}.. /{len(metric_ids)}]")
                time_series_metrics_subset = fetch_instana_infrastructure_metrics(url, token, plugin,
                                                                                  snapshots_subset, metric_ids_subset,
                                                                                  start_time, end_time, rollup)
                if time_series_metrics_subset is None:
                    continue
                if not snapshots:
                    continue
                time_series_metrics = time_series_metrics + list(time_series_metrics_subset["items"])
                metrics_count += len(time_series_metrics_subset["items"])
                if metrics_count >= limit:
                    logging.info(f"===> Reached Metrics Limit {limit}. "
                                 f"{metrics_count} metrics fetched.")
                    return time_series_metrics

    logging.info(f"===> Done. {metrics_count} metrics fetched.")
    return time_series_metrics


# Function to persist data to a file
def persist_data_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Fetch Instana metrics and events for a specified time window")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(minutes=10))
                        .strftime("%Y-%m-%dT%H:%M:%S"),
                        help="Start time in YYYY-MM-DDTHH:MM:SS format (default: last 10 minutes)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        help="End time in YYYY-MM-DDTHH:MM:SS format (default: current time)")
    parser.add_argument("--rollup", type=int, default=1,
                        help="Rollup interval in seconds (default: 1 sec)")
    parser.add_argument("--query", type=str, default="",
                        help="Query to filter snapshots by (default: Empty)")
    parser.add_argument("--plugins_filter", type=str, default="",
                        help="Filter to limit plugins to fetch (default: Empty)")
    parser.add_argument("--url", type=str, required=True, help="Instana API base URL")
    parser.add_argument("--token", type=str, required=True, help="Instana API token")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for metrics and events")
    parser.add_argument("--fetch-events", action="store_true", help="Fetch events data")
    parser.add_argument("--limit", type=int, default=1000, help="Limit the number of metrics to fetch")
    args = parser.parse_args()

    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.log_level)

    try:
        start_time = datetime.fromisoformat(args.start)
        end_time = datetime.fromisoformat(args.end)
    except ValueError:
        logging.error("Invalid time format. Please use YYYY-MM-DDTHH:MM:SS format.")
        logging.error("Invalid time format. Please use YYYY-MM-DDTHH:MM:SS format.")
        return

    # Fetch metrics from Instana API
    instana_metrics = fetch_instana_metrics(url=args.url,
                                            token=args.token,
                                            start_time=start_time,
                                            end_time=end_time,
                                            rollup=args.rollup,
                                            snapshots_query=args.query,
                                            plugins_filter=args.plugins_filter,
                                            limit=args.limit)
    if instana_metrics:
        # Persist metrics to a file
        file_name = f"{args.output_dir}/instana_metrics.json"
        persist_data_to_file(instana_metrics, file_name)
        logging.info(f"Metrics saved to {file_name}")

    if args.fetch_events:
        # Fetch events from Instana API
        logging.info("Not yet implemented")


if __name__ == "__main__":
    main()
