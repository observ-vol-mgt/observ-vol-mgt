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

logger = logging.getLogger(__name__)


def persist_data_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def fetch_instana_topology(url, token, start_time, end_time, folder):
    instana_api_url = f"{url}/api/application-monitoring/topology/services"
    result = None
    headers = {"Authorization": f"apiToken {token}", "Content-Type": "application/json"}
    params = {
        "start": int(start_time.timestamp()) * 1000,  # Convert to milliseconds
        "end": int(end_time.timestamp()) * 1000,  # Convert to milliseconds
    }
    parameters = {"applicationBoundaryScope": "ALL", 'to': params["end"], 'windowSize': params["end"] - params["start"]}
    response = requests.get(instana_api_url, params=parameters, headers=headers, verify=False)
    if response.status_code == 200:
        result = response.json()
    else:
        logging.error("Error fetching topology:", response.text)
        return
    if result != None:
        filename = f"{folder}/topology.json"
        persist_data_to_file(result, filename)
        logging.info(f"Topology saved to {folder}")


def fetch_Application_list(url, token, start_time, end_time):
    instana_api_url = f"{url}/api/application-monitoring/applications"
    result = []
    headers = {"Authorization": f"apiToken {token}", "Content-Type": "application/json"}
    params = {
        "start": int(start_time.timestamp()) * 1000,  # Convert to milliseconds
        "end": int(end_time.timestamp()) * 1000,  # Convert to milliseconds
    }
    parameters = {"applicationBoundaryScope": "ALL", 'to': params["end"], 'windowSize': params["end"] - params["start"]}
    response = requests.get(instana_api_url, params=parameters, headers=headers, verify=False)
    if response.status_code == 200:
        result = [response.json()['items']]
        total_hits = response.json()['totalHits']
        if total_hits > 1:
            for hit in range(2, total_hits):
                parameters['page'] = hit
                temp = requests.get(instana_api_url, params=parameters, headers=headers, verify=False)
                if temp.status_code == 200:
                    if len(temp.json()['items']) > 0:
                        result.append(temp.json()['items'])
                else:
                    logging.error("Error fetching topology:", temp.text)
                    break
    else:
        logging.error("Error fetching topology:", response.text)
        return
    if result != None:
        return result


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
    parser.add_argument("--token", type=str, required=True, help="Instana API token")
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
    # print(fetch_Application_list(args.url, args.token, start_time, end_time))
    fetch_instana_topology(args.url, args.token, start_time, end_time, folder=folder)


if __name__ == "__main__":
    main()
