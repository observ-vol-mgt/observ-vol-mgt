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

from common.conf import get_configuration

from common.stage import Stage

from config_generator.config_generator import config_generator
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights

output_data_dict = {}
stage_execution_order = []

# variables used for GUI of POC
signals_global = None
extracted_signals_global = None
signals_to_keep_global = None
signals_to_reduce_global = None
text_insights_global = None
r_value_global = None

def reset_globals():
    global output_data_dict
    global stage_execution_order
    output_data_dict = {}
    stage_execution_order = []


def build_pipeline():
    reset_globals() # so that tests work on a clean state of variables
    stages_params_dict = {}
    stages_pipeline_dict = {}
    configuration = get_configuration()
    pipeline = configuration['pipeline']
    parameters = configuration['parameters']
    print("pipeline = ", pipeline)
    print("parameters = ", parameters)

    # create stage structs for each of the stages
    for pa in parameters:
        s = Stage(pa)
        print("s.name = ", s.name)
        if s.name in stages_params_dict:
            raise Exception(f"duplicate stage parameters defined: {s.name}")
        stages_params_dict[s.name] = s

    print("stages = ", stages_params_dict)

    # parse pipeline section
    # connect between stages
    # check that same stage name does not appear twice in pipeline section
    for pi in pipeline:
        print("pi = ", pi)
        name = pi['name']
        if name in stages_pipeline_dict:
            raise Exception(f"stage {name} specified more than once in pipeline section")
        stages_pipeline_dict[name] = pi
        if name not in stages_params_dict:
            raise Exception(f"stage {name} not defined in parametes section")
        s = stages_params_dict[name]
        if 'follows' in pi:
            for f in pi['follows']:
                if f not in stages_params_dict:
                    raise Exception(f"stage {f} used but not defined")
                t = stages_params_dict[f]
                s.set_follows(f)
                t.add_follower(s)
        else:
            if s.input_data_fields != None and len(s.input_data_fields) > 0:
                raise Exception(f"stage {s.name} is a first stage so it should not have input data")

        # collect all the output data items in a dictionary
        global output_data_dict
        for od in s.output_data_fields:
            if od in output_data_dict:
                raise Exception(f"output_data field must be unique to a single stage: {od}")
            output_data_dict[od] = s

    # check that each follows stage actually exists
    for pi in pipeline:
        print("pi = ", pi)
        name = pi['name']
        if 'follows' in pi:
            for f in pi['follows']:
                if f not in stages_pipeline_dict:
                    raise Exception(f"stage {f} used but not declared in pipeline section")

    # decide the order in which to run the stages
    # TBD - eventually support parallel execution of tasks of DAG
    # for now, run the tasks serially. determine a legal order.
    for stage in stages_params_dict.values():
        add_stage_to_schedule(stage)


def add_stage_to_schedule(s):
    global stage_execution_order
    if s.scheduled:
        return
    for i in s.input_data_fields:
        s_prev = output_data_dict[i]
        if  not s_prev.scheduled:
            add_stage_to_schedule(s_prev)
    stage_execution_order.append(s)
    s.set_scheduled()

def run_stage(stage, input_data):
    print("stage = ", stage.name)
    attrs = vars(stage)
    print(', '.join("%s: %s" % item for item in attrs.items()))
    if stage.type == 'ingest':
        global signals_global
        signals_global = ingest(stage)
        output_data = [signals_global]
    elif stage.type == 'extract':
        global extracted_signals_global
        extracted_signals_global = feature_extraction(stage, input_data[0])
        output_data = [extracted_signals_global]
    elif stage.type == 'insights':
        global signals_to_keep_global, signals_to_reduce_global, text_insights_global
        signals_to_keep_global, signals_to_reduce_global,  text_insights_global = generate_insights(stage, input_data[0])
        output_data = [signals_to_keep_global, signals_to_reduce_global,  text_insights_global]
    elif stage.type == 'config_generator':
        global r_value_global
        r_value_global = config_generator(stage, input_data[0], input_data[1], input_data[2])
        output_data = [r_value_global]
    else:
        str = "stage type not implemented: " + stage.type
        raise Exception(f"stage type not implemented: {stage.type}")
    stage.set_latest_output_data(output_data)


def run_iteration():
    for s in stage_execution_order:
        # gather the input data
        input_data = []
        print("fields = ", s.input_data_fields)
        for i_field in s.input_data_fields:
            print("i = ", i_field)
            # find the stage where that input field is generated
            s_prev = output_data_dict[i_field]
            print("s_prev = ", s_prev)
            attrs = vars(s_prev)
            print(', '.join("%s: %s" % item for item in attrs.items()))
            #  latest_output_data contains a list of outputs; select the right one
            for o_field in s_prev.output_data_fields:
                if o_field == i_field:
                    index = s_prev.output_data_fields.index(o_field)
                    break
            input_data.append(s_prev.latest_output_data[index])
        run_stage(s, input_data)

