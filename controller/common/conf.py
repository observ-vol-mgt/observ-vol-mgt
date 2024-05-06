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
from common.stage import stage

args = None
configuration = None
stages_dict = None
first_stage = None

def get_args():
    return args

def get_configuration():
    return configuration

def get_first_stage():
    return first_stage

def parse_args():
    p = configargparse.ArgParser()
    p.add('-c', '--config-file', help='config file path',
          default='config.yaml', env_var='CONFIGFILE')
    p.add('-v', '--loglevel', help='logging level',
          default='info', env_var='LOGLEVEL')
    p.add('--config_generator_type', help='configuration generation type (none, otel or processor)',
          default = 'none', env_var = 'CONFIG_GENERATOR_TYPE')
    p.add('--config_generator_directory', help='configuration generation output directory',
          default='/tmp', env_var = 'CONFIG_GENERATOR_DIR')

    global args
    args = p.parse_args()
    print(args)
    print("----------")
    print(p.format_help())
    print("----------")
    print(p.format_values())

    with open(args.config_file, 'r') as file:
        global configuration
        configuration = yaml.safe_load(file)
        print("----------")
        print("Configuration")
        print(configuration)

    build_pipeline()

def build_pipeline():
    pipeline = configuration['pipeline']
    parameters = configuration['parameters']
    stages = {}
    # create stage structs for each of the stages
    for pa in parameters:
        s = stage(pa)
        stages[s.name] = s

    global stages_dict
    stages_dict = stages
    print("stages = ", stages)

    # parse pipeline section
    # find first stage and connect between stages
    for pi in pipeline:
        print("pi = ", pi)
        name = pi['name']
        s = stages[name]
        if 'follows' in pi:
            f_stage = stages[pi['follows']]
            s.set_follows(f_stage)
            f_stage.add_follower(s)
            n = min(len(s.input_data_types), len(f_stage.output_data_types))
            for i in range(n):
                if s.input_data_types[i] != f_stage.output_data_types[i]:
                    str = "mismatch of data types between stages {s.name} and {f_stage.name}; {f_stage.input_data_types[i]}, {s.output_data_types[i]}"
                    raise str
        else:
            global first_stage
            if first_stage != None:
                raise "only one initial stage is allowed"
            first_stage = s
            print("first stage = ", first_stage.name)
