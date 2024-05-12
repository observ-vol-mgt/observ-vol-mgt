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

from workflow_orchestration.stage import StageParameters

from config_generator.config_generator import config_generator
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights
from common.configuration_api import TYPE_INGEST, TYPE_EXTRACT, TYPE_INSIGHTS, TYPE_CONFIG_GENERATOR

import logging
logger = logging.getLogger(__name__)

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
    stages_parameters = configuration['parameters']

    # create stage structs for each of the stages
    for stage_params in stages_parameters:
        stg = StageParameters(stage_params)
        if stg.name in stages_params_dict:
            raise Exception(f"duplicate stage parameters defined: {stg.name}")
        stages_params_dict[stg.name] = stg
    logger.info(f"stages = {stages_params_dict}")

    # parse pipeline section
    # connect between stages
    # check that same stage name does not appear twice in pipeline section
    for pip_stage in pipeline:
        name = pip_stage['name']
        if name in stages_pipeline_dict:
            raise Exception(f"stage {name} specified more than once in pipeline section")
        stages_pipeline_dict[name] = pip_stage
        if name not in stages_params_dict:
            raise Exception(f"stage {name} not defined in parametes section")
        stg = stages_params_dict[name]
        if 'follows' in pip_stage:
            for f in pip_stage['follows']:
                if f not in stages_params_dict:
                    raise Exception(f"stage {f} used but not defined")
                t = stages_params_dict[f]
                stg.set_follows(f)
                t.add_follower(stg)
        else:
            if stg.input_data_fields != None and len(stg.input_data_fields) > 0:
                raise Exception(f"stage {stg.name} is a first stage so it should not have input data")

        # collect all the output data items in a dictionary
        global output_data_dict
        for od in stg.output_data_fields:
            if od in output_data_dict:
                raise Exception(f"output_data field must be unique to a single stage: {od}")
            output_data_dict[od] = stg

    # check that each follows stage actually exists
    for pip_stage in pipeline:
        if 'follows' in pip_stage:
            for f in pip_stage['follows']:
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
    if stage.type == TYPE_INGEST:
        global signals_global
        signals_global = ingest(stage.subtype, stage.config)
        output_data = [signals_global]
    elif stage.type == TYPE_EXTRACT:
        global extracted_signals_global
        extracted_signals_global = feature_extraction(stage.subtype, stage.config, input_data[0])
        output_data = [extracted_signals_global]
    elif stage.type == TYPE_INSIGHTS:
        global signals_to_keep_global, signals_to_reduce_global, text_insights_global
        signals_to_keep_global, signals_to_reduce_global,  text_insights_global = generate_insights(stage.subtype, stage.config, input_data[0])
        output_data = [signals_to_keep_global, signals_to_reduce_global,  text_insights_global]
    elif stage.type == TYPE_CONFIG_GENERATOR:
        global r_value_global
        r_value_global = config_generator(stage.subtype, stage.config, input_data[0], input_data[1], input_data[2])
        output_data = [r_value_global]
    else:
        raise Exception(f"stage type not implemented: {stage.type}")
    stage.set_latest_output_data(output_data)


def run_iteration():
    for s in stage_execution_order:
        # gather the input data
        input_data = []
        for i_field in s.input_data_fields:
            # find the stage where that input field is generated
            s_prev = output_data_dict[i_field]
            #  latest_output_data contains a list of outputs; select the right one
            for o_field in s_prev.output_data_fields:
                if o_field == i_field:
                    index = s_prev.output_data_fields.index(o_field)
                    break
            input_data.append(s_prev.latest_output_data[index])
        run_stage(s, input_data)

