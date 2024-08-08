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

from flask import Flask, request, jsonify
from scripts.update_otel_collector_configuration import update_processors
from scripts.restart_docker_container import restart_docker_container
import os
import argparse
import logging
import yaml

app = Flask(__name__)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/delete', methods=['POST'])
def reset_yaml():
    try:
        ## TODO: [ER] change this code so it will not be hard coded and will be used from the original file
        data = """processors:
  metricstransform:
    transforms:
      - include: .*
        match_type: regexp
        action: update
        operations:
          - action: experimental_scale_value
            experimental_scale: 1
"""
        data = yaml.safe_load(data)
        result = execute_update(data)
        return result
    except Exception as e:
        logger.error(f"Failed to save YAML file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/create', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_yaml():
    try:
        if not request.data:
            logger.warning("No data received")
            return jsonify({"error": "No data received"}), 400

        data = yaml.safe_load(request.data.decode('utf-8'))
        result = execute_update(data)
        return result
    except Exception as e:
        logger.error(f"Failed to save YAML file: {e}")
        return jsonify({"error": str(e)}), 500


def execute_update(data):
    try:
        if data is None:
            logger.warning("No YAML data received")
            return jsonify({"error": "No YAML data received"}), 400

        with open(args.save_update_path, 'w') as file:
            yaml.dump(data, file)

        logger.info(f"YAML file saved to {args.save_update_path}")

        update_processors(args.processor_file_to_update, args.save_update_path, args.processor_file_to_update)
        logger.info(f"Processors section in YAML file {args.processor_file_to_update} updated")

        if args.docker_container_reset_on_update != "":
            restart_docker_container(args.docker_container_reset_on_update)
            logger.info(f"Docker container {args.docker_container_reset_on_update} restarted")

        return jsonify({"message": "YAML file saved successfully"}), 200
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file: {e}")
        return jsonify({"error": f"Failed to parse YAML file: {e}"}), 400
    except Exception as e:
        logger.error(f"Failed to save YAML file: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask JSON Upload Server")
    parser.add_argument('--save-update-path', type=str, required=True,
                        help='Path where the updated YAML file will be saved')
    parser.add_argument('--processor-file-to-update', type=str, required=True,
                        help='oTel collector YAML file path - to be updated')
    parser.add_argument('--docker-container-reset-on-update', type=str, required=True,
                        help='The name of the Docker container to reset on update')
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.save_update_path), exist_ok=True)

    logger.info(f"Starting server \n------\n"
                f"save_update_path: {args.save_update_path}\n"
                f"processor-file-to-update: {args.processor_file_to_update}\n"
                f"docker-container-reset-on-update: {args.docker_container_reset_on_update}\n")
    app.run(host='0.0.0.0', port=5000)
