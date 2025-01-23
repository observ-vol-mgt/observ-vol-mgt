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
import time

import requests
import json
import argparse
from datetime import datetime, timedelta

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_instana_application_catalog(url, token):
    instana_api_url = f"{url}/api/application-monitoring/catalog/metrics"

    headers = {
        "Authorization": f"apiToken {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(instana_api_url, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Error fetching plugins:", response.text)
        return None


def fetch_instana_application_metrics(url, token, metric_ids, start_time, end_time, granularity=1):
    instana_api_url = f"{url}/api/application-monitoring/metrics/applications"

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
        metrics = [{"metric": i, "aggregation": "PER_SECOND", "granularity": granularity} for i in metric_ids]
        body = {
            "metrics": metrics,
            "order": {"by": "timestamp", "direction": "DESC"},
            "timeFrame": {"to": params["end"], "windowSize": params["end"] - params["start"],
                          "pagination": {"page": 1, "pageSize": 200}},
        }
        parameters = {'offline': True}
        response = requests.post(instana_api_url, params=parameters, headers=headers, json=body, verify=False)
        if response.status_code == 200:
            result.append(response.json()["items"])
            total_hits = response.json()['totalHits']
            if total_hits > 1:
                logging.info(f"\tFound data in {total_hits} pages")
                for page in range(2, total_hits):
                    body['pagination'] = {"page": page, "pageSize": 200}
                    response = requests.post(instana_api_url, params=parameters, headers=headers, json=body,
                                             verify=False)
                    if response.status_code == 200:
                        result.append(response.json()["items"])
                    else:
                        logging.error("Error fetching metrics:", response.text)
                        continue
        else:
            logging.error("Error fetching metrics:", response.text)
            continue
        s_time = e_time

    return result


def fetch_instana_metrics(url, token, start_time, end_time, granularity=1, folder="data"):
    metrics_catalog = fetch_instana_application_catalog(url, token[0])
    if metrics_catalog is None:
        logging.error(f"No application metrics available")
        return

    metric_ids = list(map(lambda item: item['metricId'], metrics_catalog))

    metrics_api_limit = 5
    counter = 0

    for i in range(0, len(metric_ids), metrics_api_limit):
        token_ins = token[counter % len(token)]
        metric_ids_subset = metric_ids[i:i + metrics_api_limit]
        logging.info(f"metrics: [{i}.. /{len(metric_ids)}]")
        time_series_metrics_subset = fetch_instana_application_metrics(url, token_ins, metric_ids_subset, start_time,
                                                                       end_time, granularity)
        if time_series_metrics_subset is None:
            time.sleep(10)
            return
        time.sleep(1)
        counter += 1
        file_name = f"{folder}/instana_application_metrics_{i}.json"
        persist_data_to_file(time_series_metrics_subset, file_name)
        logging.info(f"Metrics saved to {file_name}")


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
    parser.add_argument("--url", type=str, required=True, help="Instana API base URL")
    parser.add_argument("--token", nargs='+', type=str, required=True, help="Instana API token")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for metrics and events")

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

    folder = args.output_dir
    fetch_instana_metrics(args.url, args.token, start_time, end_time, granularity=60, folder=folder)


if __name__ == "__main__":
    main()
