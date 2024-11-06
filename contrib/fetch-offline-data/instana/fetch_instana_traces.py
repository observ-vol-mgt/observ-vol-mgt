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


def fetch_instana_traces(url, token, start_time, end_time, service_name_filter, output_dir,
                         traces_limit=None, include_internal=False, include_synthetic=False):

    # 1. We will first get the list of traces (without details)
    instana_api_url = f"{url}/api/application-monitoring/analyze/traces"
    result = None
    headers = {"Authorization": f"apiToken {token}", "Content-Type": "application/json"}
    params = {
        "start": int(start_time.timestamp()) * 1000,  # Convert to milliseconds
        "end": int(end_time.timestamp()) * 1000,  # Convert to milliseconds
    }
    data = {"tagFilterExpression": {"type": "TAG_FILTER", "name": "service.name", "operator": "EQUALS",
                                    "entity": "DESTINATION", "value": service_name_filter},
            'timeFrame': {'to': params["end"], 'windowSize': params["end"] - params["start"]},
            "includeInternal": include_internal, "includeSynthetic": include_synthetic}
    response = requests.post(instana_api_url, data=json.dumps(data), headers=headers, verify=False)
    if response.status_code == 200:
        result = response.json()
    else:
        logging.error("Error fetching traces:", response.text)
        return

    traces = result['items'][:traces_limit] if traces_limit is not None else result['items']
    # 2. For each item in the result list, we will get additional details
    for trace in traces:
        instana_api_url = f"{url}/api/application-monitoring/v2/analyze/traces/{trace['trace']['id']}"
        response = requests.get(instana_api_url, headers=headers, verify=False)
        if response.status_code == 200:
            trace['details'] = response.json()

    if result is not None:
        filename = f"{output_dir}/traces.json"
        persist_data_to_file(traces, filename)
        logging.info(f"Traces saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Instana traces for a specified time window")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(minutes=10))
                        .strftime("%Y-%m-%dT%H:%M:%S"),
                        help="Start time in YYYY-MM-DDTHH:MM:SS format (default: last 10 minutes)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        help="End time in YYYY-MM-DDTHH:MM:SS format (default: current time)")
    parser.add_argument("--url", type=str, required=True, help="Instana API base URL")
    parser.add_argument("--token", type=str, required=True, help="Instana API token")
    parser.add_argument("--service_name_filter", default=None, type=str, help="Service name filter for traces")
    parser.add_argument("--include_internal", default=False, type=bool, help="Include internal traces")
    parser.add_argument("--include_synthetic", default=False, type=bool, help="Include synthetic traces")
    parser.add_argument("--traces_limit", default=None, type=int, help="Maximum number of traces to dump")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for traces")

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

    output_dir = args.output_dir
    service_name_filter = args.service_name_filter
    traces_limit = args.traces_limit
    fetch_instana_traces(args.url, args.token, start_time, end_time,
                         service_name_filter=service_name_filter, output_dir=output_dir,
                         traces_limit=traces_limit)


if __name__ == "__main__":
    main()
