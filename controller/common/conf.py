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
import yaml

args = None
configuration = None


def get_args():
    return args


def get_configuration():
    return configuration


def set_configuration(config):
    global configuration
    configuration = config


def parse_args():
    p = configargparse.ArgParser()
    p.add('-c', '--config-file', help='config file path',
          default='config.yaml', env_var='CONFIGFILE')
    p.add('--noui', help='dont expose ui', action='store_true',
          default=False, env_var='NOUI')
    p.add('-v', '--loglevel', help='logging level',
          default='info', env_var='LOGLEVEL')

    global args
    args = p.parse_args()
    print(args)

    with open(args.config_file, 'r') as file:
        configuration = yaml.safe_load(file)
        set_configuration(configuration)
        print("----------")
        print("Configuration")
        print(configuration)
