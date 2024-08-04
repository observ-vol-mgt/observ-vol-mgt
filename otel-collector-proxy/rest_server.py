# server.py
from flask import Flask, request, jsonify
from scripts.update_otel_collector_configuration import update_processors
import os
import argparse
import logging
import yaml

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/create', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_yaml():
    try:
        if not request.data:
            logger.warning("No data received")
            return jsonify({"error": "No data received"}), 400

        data = yaml.safe_load(request.data.decode('utf-8'))
        if data is None:
            logger.warning("No YAML data received")
            return jsonify({"error": "No YAML data received"}), 400

        with open(args.save_update_path, 'w') as file:
            yaml.dump(data, file)

        logger.info(f"YAML file saved to {args.save_update_path}")

        update_processors(args.processor_file_to_update, args.save_update_path, args.processor_file_to_update)
        logger.info(f"Processors section in YAML file {args.processor_file_to_update} updated")

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
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.save_update_path), exist_ok=True)

    logger.info(f"Starting server "
                f"with save_update_path: {args.save_update_path} and "
                f"processor-file-to-update: {args.processor_file_to_update}")
    app.run(host='0.0.0.0', port=5000)
