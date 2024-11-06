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


import json
import argparse
import logging
import os

logger = logging.getLogger(__name__)


def persist_data_to_file(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def parse_instana_traces(input_file, output_dir):
    with open(input_file, 'r') as infile:
        traces = json.load(infile)

    queries = []
    for trace in traces:
        try:
            details = trace.get('details', {})
            items = details.get('items', [])
            for item in items:
                name = item.get('name')
                try:
                    name_json = json.loads(name)
                    if isinstance(name_json, dict) and 'queries' in name_json:
                        name_json['trace_id'] = item.get('id')
                        queries.append(name_json)
                except json.JSONDecodeError:
                    continue
        except ValueError:
            continue

    if queries is not None:
        filename = f"{output_dir}/queries.json"
        persist_data_to_file(queries, filename)
        logging.info(f"Queries (parsed from traces) saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Fetch Instana traces for a specified time window")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--input_file", default="traces.json", type=str, help="Input instana json traces file")
    parser.add_argument("--output_dir", default=os.getcwd(), type=str, help="Output directory for parsed traces")

    args = parser.parse_args()

    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.log_level)

    parse_instana_traces(args.input_file, args.output_dir)


if __name__ == '__main__':
    main()
