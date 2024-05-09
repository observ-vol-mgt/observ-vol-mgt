import logging
import os

import requests
import json
import argparse
from datetime import datetime, timedelta


def check_value_in_list_of_dicts(value, list_of_dicts):
    for d in list_of_dicts:
        for v in d.values():
            if value == v:
                return True
    return False


def fetch_instana_plugins_catalog(url, token):
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
        return response.json()
    else:
        print("Error fetching plugins:", response.text)
        return None


def fetch_instana_snapshots(url, token, plugin, start_time, end_time):
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
                  'windowSize': params["end"] - params["start"]}

    # fetch metrics
    response = requests.get(instana_api_url, params=parameters, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return list(map(lambda item: item['snapshotId'], response.json()['items']))
    else:
        print("Error fetching plugins:", response.text)
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
        print("Error fetching plugins:", response.text)
        return None


# fetch metrics from Instana API
def fetch_instana_infrastructure_metrics(url, token, plugin, snapshots, metric_ids, start_time,  end_time, granularity=1):

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
        'rollup': granularity,
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
        print("Error fetching metrics:", response.text)
        return None


def fetch_instana_metrics(url, token, start_time, end_time, granularity=1):
    plugins = fetch_instana_plugins_catalog(url, token)
    if plugins is None:
        return None
    if not check_value_in_list_of_dicts("prometheus", plugins):
        return None
    plugin = "prometheus"  # <<<--- for now only prometheus

    snapshots = fetch_instana_snapshots(url, token, plugin, start_time, end_time)
    if snapshots is None:
        return None
    snapshots = snapshots[:30]  # <<<--- for now only first 30 (limitation of the API)

    metrics_catalog = fetch_instana_metrics_catalog(url, token, plugin)
    if metrics_catalog is None:
        return None
    metric_ids = list(map(lambda item: item['metricId'], metrics_catalog))

    metric_ids = metric_ids[:5]  # <<<--- for now only first 5 (limitation of the API)

    time_series_metrics = fetch_instana_infrastructure_metrics(url, token, plugin, snapshots, metric_ids,
                                                               start_time, end_time, granularity)
    if time_series_metrics is None:
        return None

    return time_series_metrics


# Function to persist data to a file
def persist_data_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Fetch Instana metrics and events for a specified time window")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(minutes=10))
                        .strftime("%Y-%m-%dT%H:%M:%S"),
                        help="Start time in YYYY-MM-DDTHH:MM:SS format (default: last 10 minutes)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        help="End time in YYYY-MM-DDTHH:MM:SS format (default: current time)")
    parser.add_argument("--url", type=str, required=True, help="Instana API base URL")
    parser.add_argument("--token", type=str, required=True, help="Instana API token")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for metrics and events")
    parser.add_argument("--fetch-events", action="store_true", help="Fetch events data")
    args = parser.parse_args()

    try:
        start_time = datetime.fromisoformat(args.start)
        end_time = datetime.fromisoformat(args.end)
    except ValueError:
        print("Invalid time format. Please use YYYY-MM-DDTHH:MM:SS format.")
        return

    # Fetch metrics from Instana API
    instana_metrics = fetch_instana_metrics(args.url, args.token, start_time, end_time)
    if instana_metrics:
        # Persist metrics to a file
        file_name = f"{args.output_dir}/instana_metrics.json"
        persist_data_to_file(instana_metrics, file_name)
        print(f"Metrics saved to {file_name}")

    if args.fetch_events:
        # Fetch events from Instana API
        print("Not yet implemented")


if __name__ == "__main__":
    main()
