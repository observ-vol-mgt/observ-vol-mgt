#   Copyright 2024 IBM, Inc.
#  #
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  #
#       http://www.apache.org/licenses/LICENSE-2.0
#  #
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import argparse
import json
import logging
import os

logger = logging.getLogger(__name__)


def convert_to_promql_format(src_json_file, dst_promql_file):
    try:
        # Read the Instana metrics from the input file
        with open(src_json_file, "r") as src_file:
            data = json.load(src_file)

        # Write the PromQL metrics to the output file
        with open(dst_promql_file, "w") as dst_file:
            # Write the Header
            dst_file.write('''{
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [''')
            # Write the PromQL metrics to the output file
            for snapshot_metrics in data:
                for metric, time_series in snapshot_metrics['metrics'].items():
                    time_series_milisec_timetamps = [[point[0]/1000, point[1]] for point in time_series]
                    dst_file.write(f'''
                {{
                    "metric": {{
                        "__name__": "{metric}",
                        "instance": "{snapshot_metrics["host"]}",
                        "plugin": "{snapshot_metrics["plugin"]}",
                        "label": "{snapshot_metrics["label"]}",
                        "snapshotId": "{snapshot_metrics["snapshotId"]}",
                        "job": "prometheus"
                        }},
                    "values":
                        {time_series_milisec_timetamps}
                }},''')
            # Write the Footer
            dst_file.flush()
            file_size = os.path.getsize(dst_promql_file)
            dst_file.seek(file_size-1)
            dst_file.write('''
    ]
  }
}
''')
        return True
    except Exception as e:
        logger.error(f"Error converting Instana metrics to PromQL format: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert Instana metrics dump json file to PromQL dump metrics file")
    parser.add_argument("--log-level", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        default="INFO", help="Logging level (default: INFO)")
    parser.add_argument("--src_json_file", type=str,
                        default="instana_metrics.json", help="Instana API metrics file (Input)")
    parser.add_argument("--dst_promql_file", type=str,
                        default="promql_metrics.json", help="PromQL metrics file (output)")
    args = parser.parse_args()

    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=args.log_level)

    status = convert_to_promql_format(args.src_json_file, args.dst_promql_file)
    if not status:
        logging.error("Failed to convert Instana metrics to PromQL format")
        return

    logging.info("Instana metrics converted to PromQL format")
    logging.info(f"PromQL metrics saved to {args.dst_promql_file}")
    logging.info("Done")


if __name__ == "__main__":
    main()
