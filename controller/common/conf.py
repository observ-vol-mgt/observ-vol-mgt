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

import configargparse

configuration = None


def get_configuration():
    return configuration


def parse_configuration():
    p = configargparse.ArgParser(
        default_config_files=['~/controller.config.yaml', 'config.yaml'])
    p.add('-c', '--config-file', required=False,
          is_config_file=True, help='config file path')
    p.add('-v', '--loglevel', help='logging level',
          default='info', env_var='LOGLEVEL')
    p.add('--ingest_type', help='ingest type (dummy, file or promql)',
          default='dummy', env_var='INGEST_TYPE')
    p.add('--ingest_file', help='ingest file ( for file type )',
          env_var='INGEST_FILE')
    p.add('--ingest_url', help='ingest url ( for promql type )',
          env_var='INGEST_URL')
    p.add('--ingest_window', help='ingest window ( for promql type )',
          env_var='INGEST_WINDOW')
    p.add('--feature_extraction_type', help='feature_extraction type (tsfel or tsfresh)',
          env_var='FEATURE_EXTRACTION_TYPE')
    p.add('--config_generator_type', help='configuration generation type (none, otel or processor)',
          default='none', env_var='CONFIG_GENERATOR_TYPE')
    p.add('--config_generator_directory', help='configuration generation output directory',
          env_var='CONFIG_GENERATOR_DIR')

    global configuration
    configuration = p.parse_args()
    print(configuration)
    print("----------")
    print(p.format_help())
    print("----------")
    print(p.format_values())
