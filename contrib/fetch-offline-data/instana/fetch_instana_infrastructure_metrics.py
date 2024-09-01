import logging
import os
import time

import requests
import json
import argparse
from datetime import datetime, timedelta

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def format_metric_id(metric):
    j = {}
    try:
        if '{' in metric:
            metric_name, tags = metric.split('{')
        else:
            metric_name, tags = metric, None
        metric_name = metric_name.split('.')[2]
        j['metric'] = metric_name

        if tags == None:
            return j

        tags = tags.strip('}')
        for label in tags.split(','):
            key, value = label.split("=")
            key = key.strip()
            value = value.strip().strip('"')
            j[key] = value
        return j
    except:
        return None


def select(metric, query):
    metric_details = format_metric_id(metric)

    if metric_details != None:
        for field in query:
            if field not in metric_details:
                return False
            else:
                if metric_details[field] not in query[field]:
                    return False
        return True
    return False


def filter_metric_ids(metric_ids, query):
    selected_metric = []
    for metric in metric_ids:
        if select(metric, query):
            selected_metric.append(metric)
    return selected_metric


def fetch_instana_plugins_catalog(url, token):
    # Instana API endpoint for fetching plugins
    instana_api_url = f"{url}/api/infrastructure-monitoring/catalog/plugins"

    # Define headers with the API token
    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    # Make a GET request to fetch plugins
    response = requests.get(instana_api_url, headers=headers, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching plugins:", response.text)
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
    response = requests.get(instana_api_url, params=parameters, headers=headers, verify=False)

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
    response = requests.get(instana_api_url, headers=headers, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


def fetch_instana_infrastructure_metrics(url, token, plugin, snapshots, metric_ids, start_time, end_time,
                                         granularity=1):
    # Instana API endpoint for fetching metrics
    instana_api_url = f"{url}/api/infrastructure-monitoring/metrics"

    s_time = int(start_time.timestamp()) * 1000
    f_time = int(end_time.timestamp()) * 1000
    result = []
    while s_time < f_time:
        e_time = s_time + granularity * 600 * 1000
        logging.info(f"Getting metric from {s_time} to {e_time}")
        params = {
            "start": s_time,  # Convert to milliseconds
            "end": e_time,  # Convert to milliseconds
        }

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
        response = requests.post(instana_api_url, params=parameters, headers=headers, json=body, verify=False)
        if response.status_code == 200:
            result.append(response.json()["items"])
        else:
            logging.error("Error fetching metrics:", response.text)
            continue
        s_time = e_time

    return result


def fetch_instana_metrics(url, token, start_time, end_time, plugin, granularity=1, filter_query={}, folder="data"):
    time_series_metrics = []
    metrics_count = 0
    plugins_catalog = fetch_instana_plugins_catalog(url, token[0])
    if plugins_catalog is None:
        return None

    plugins = list(map(lambda item: item['plugin'], plugins_catalog))
    if plugin != None and plugin not in plugins:
        logging.error(f"Plugin with name {plugin} not available.")
        return None

    if plugin != None:
        plugins = [plugin]

    # for each plugin, fetch snapshots and metrics
    for p in range(0, len(plugins)):
        plugin = plugins[p]
        logging.info(f"fetching metrics for plugin: {plugin} [{p}/{len(plugins)}]")

        # fetch the snapshots
        snapshots = fetch_instana_snapshots(url, token[0], plugin, start_time, end_time)
        if not snapshots:
            continue

        # fetch the metric ids
        metrics_catalog = fetch_instana_metrics_catalog(url, token[0], plugin)
        if metrics_catalog is None:
            continue

        # print(json.dumps(metrics_catalog))
        # return

        metric_ids = list(map(lambda item: item['metricId'], metrics_catalog))

        logging.info(f"Applying filter : {filter_query}")

        if filter_query != {}:
            filtered_metric_ids = filter_metric_ids(metric_ids, filter_query)
            metric_ids = filtered_metric_ids

        # fetch the time_series metrics
        metrics_api_limit = 5  # <<<--- limitation of the API to max 5 metrics per call
        snapshots_api_limit = 30  # <<<--- limitation of the API to max 30 snapshots per call
        # tokens = ["tMd8pw4WS6SdLkx1QI2KeQ", "tmdOVgSMS7ucB2rCOXkvLg", "y7l5tD1wR9G581LYOfYxKQ"]
        counter = 0
        for i in range(0, len(snapshots), snapshots_api_limit):
            snapshots_subset = snapshots[i:i + snapshots_api_limit]
            for j in range(0, len(metric_ids), metrics_api_limit):
                token_ins = token[counter % len(token)]
                metric_ids_subset = metric_ids[j:j + metrics_api_limit]
                logging.info(f"=> fetching time series for plugin: {plugin}, "
                             f"snapshots: [{i}.. /{len(snapshots)}] "
                             f"metrics: [{j}.. /{len(metric_ids)}]")
                time_series_metrics_subset = fetch_instana_infrastructure_metrics(url, token_ins, plugin,
                                                                                  snapshots_subset, metric_ids_subset,
                                                                                  start_time, end_time,
                                                                                  granularity)
                if not snapshots:
                    continue
                time_series_metrics = time_series_metrics + time_series_metrics_subset
                metrics_count += len(time_series_metrics_subset)
                time.sleep(1)
                counter += 1
            file_name = f"{folder}/{plugin}_instana_infrastructure_metrics_{i}.json"
            persist_data_to_file(time_series_metrics, file_name)
            logging.info(f"Metrics saved to {file_name}")
            time_series_metrics = []

    logging.info(f"===> Done. {metrics_count} metrics fetched.")
    return time_series_metrics


def persist_data_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def parse_args_to_dict(query_string):
    if query_string == None or query_string == "":
        return {}
    query = {}
    try:
        s = query_string.strip()
        s = s.split(",")
        for e in s:
            key, value = e.split("=")
            query[key] = value
    except Exception as e:
        logging.error("Error while parsing input query to json :", e)
    return query


def main():
    parser = argparse.ArgumentParser(description="Fetch Instana metrics and events for a specified time window")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(minutes=10))
                        .strftime("%Y-%m-%dT%H:%M:%S"),
                        help="Start time in YYYY-MM-DDTHH:MM:SS format (default: last 10 minutes)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        help="End time in YYYY-MM-DDTHH:MM:SS format (default: current time)")
    parser.add_argument("--url", type=str, required=True, help="Instana API base URL")
    parser.add_argument("--token", nargs='+', type=str, required=True, help="Instana API token")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for metrics and events")
    parser.add_argument("--plugin", type=str, default=None, help="Fetch metrics for user provided plugin")
    parser.add_argument("--query", type=str, default=None, help="Fetch metrics which satisfies query")
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

    filter_query = parse_args_to_dict(args.query)

    folder = args.output_dir

    instana_metrics = fetch_instana_metrics(args.url, args.token, start_time, end_time, args.plugin,
                                            filter_query=filter_query, granularity=60, folder=folder)
    if instana_metrics:
        file_name = f"{folder}/instana_metrics_final.json"
        persist_data_to_file(instana_metrics, file_name)
        logging.info(f"Metrics saved to {file_name}")


if __name__ == "__main__":
    main()
