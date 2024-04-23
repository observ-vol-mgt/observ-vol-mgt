import os
import logging
import yaml

logger = logging.getLogger(__name__)

def load_processors(processor_urls, processors_folder):
    processor_ids = []
    for key, value in processor_urls.items():
        processor_id = f"{key}".split('_URL')[0].split('PROCESSOR_')[1]
        file_path = os.path.join(f"{processors_folder}", f"{processor_id}.yaml")
        file_path = f"{processors_folder}/{processor_id}.yaml"

        if processor_id not in processor_ids:
            processor_ids.append(processor_id)
        else:
            logger.error(f"Duplicate URL provided for processor with id {processor_id}, we will be using the previously specified URL")
            continue

        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                pass  # Do nothing, file created and closed immediately

    return processor_ids


def create_or_replace_processor_file(processors_folder, processor_id, processor_data):
    file_path = os.path.join(f"{processors_folder}", f"{processor_id}.yaml")
    with open(file_path, 'w') as file:
        file.write(processor_data)

def delete_processor_file(processors_folder, processor_id):
    file_path = os.path.join(f"{processors_folder}", f"{processor_id}.yaml")
    # Replace the content of the YAML file with an empty YAML content
    with open(file_path, 'w') as file:
        file.write("")

def read_processor_file(processors_folder, processor_id):
    processor_file = f"{processors_folder}/{processor_id}.yaml"
    with open(processor_file, 'r') as file:
        return yaml.safe_load(file)
