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

import yaml
import logging

logger = logging.getLogger(__name__)


def update_processors(main_config_path, update_config_path, output_path):
    try:
        logging.info(f'Reading main configuration from {main_config_path}')
        with open(main_config_path, 'r') as main_file:
            main_config = yaml.safe_load(main_file)

        logging.info(f'Reading update configuration from {update_config_path}')
        with open(update_config_path, 'r') as update_file:
            update_config = yaml.safe_load(update_file)

        # Replace the processors section
        logging.info('Updating processors section in the main configuration')
        main_config['processors'] = update_config['processors']

        # Update the processors pipline section
        logging.info('Updating pipline')
        main_config['service']['pipelines']['metrics/1']['processors'] = list(main_config['processors'].keys())

        logging.info(f'Writing updated configuration to {output_path}')
        with open(output_path, 'w') as output_file:
            yaml.safe_dump(main_config, output_file)

        logging.info('Configuration update completed successfully')

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise
