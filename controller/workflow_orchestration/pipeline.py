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

from workflow_orchestration.stage import StageParameters, BaseStageParameters, PipelineDefinition

from config_generator.config_generator import config_generator
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights
from common.configuration_api import StageType
from split.split import split
from merge.merge import merge
import common.configuration_api as api
import copy

import logging
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self):
        self.output_data_dict = {}
        self.stage_execution_order = []


        # variables used for GUI of POC
        self.signals = None
        self.extracted_signals = None
        self.signals_to_keep = None
        self.signals_to_reduce = None
        self.text_insights = None
        self.r_value = None

    def build_pipeline(self):
        stages_params_dict = {}
        stages_pipeline_dict = {}
        configuration = get_configuration()
        pipeline = configuration['pipeline']
        stages_parameters = configuration['parameters']

        # verify that configuration is valid
        # if not valid, the following line will throw an exception
        PipelineDefinition(**configuration)

        # create stage structs for each of the stages
        for stage_params in stages_parameters:
            stg = StageParameters(stage_params)
            if stg.base_stage.name in stages_params_dict:
                raise Exception(f"duplicate stage parameters defined: {stg.base_stage.name}")
            stages_params_dict[stg.base_stage.name] = stg
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
                if stg.base_stage.input_data != None and len(stg.base_stage.input_data) > 0:
                    raise Exception(f"stage {stg.base_stage.name} is a first stage so it should not have input data")

            # collect all the output data items in a dictionary
            for od in stg.base_stage.output_data:
                if od in self.output_data_dict:
                    raise Exception(f"output_data field must be unique to a single stage: {od}")
                self.output_data_dict[od] = stg

        # check that each follows stage actually exists
        for pip_stage in pipeline:
            if 'follows' in pip_stage:
                for f in pip_stage['follows']:
                    if f not in stages_pipeline_dict:
                        raise Exception(f"stage {f} used but not declared in pipeline section")

        # for each multi_stage, verify it follows a single previous split or multi_stage
        for stg in stages_params_dict.values():
            if stg.base_stage.multi_stage:
                if len(stg.follows) != 1:
                    raise Exception(f"multi_stage {stg.base_stage.name} must follow a single other stage")
                prev_stage = stages_params_dict[stg.follows[0]]
                if not prev_stage.base_stage.multi_stage and prev_stage.base_stage.type != api.StageType.SPLIT.value:
                    raise Exception(f"multi_stage {stg.base_stage.name} must follow a multi_stage or a split")
                if len(stg.base_stage.input_data) != 1:
                    raise Exception(f"multi_stage {stg.base_stage.name} may have only one input list")
                if len(stg.base_stage.output_data) != 1:
                    raise Exception(f"multi_stage {stg.base_stage.name} may have only one output list")

        # decide the order in which to run the stages
        # support for parallel execution of tasks of DAG performed elsewhere (during execution of DAG)
        # for now, run the tasks serially. determine a legal order.
        for stage in stages_params_dict.values():
            self.add_stage_to_schedule(stage)


    def add_stage_to_schedule(self, s):
        if s.scheduled:
            return
        for i in s.base_stage.input_data:
            s_prev = self.output_data_dict[i]
            if  not s_prev.scheduled:
                self.add_stage_to_schedule(s_prev)
        self.stage_execution_order.append(s)
        s.set_scheduled()

    def run_stage(self, stage, input_data):
        attrs = vars(stage)
        print("run_stage, stage = ", attrs)
        print("run_stage, len of input_data = ", len(input_data))
        if stage.base_stage.type == StageType.INGEST.value:
            self.signals = ingest(stage.base_stage.subtype, stage.base_stage.config)
            output_data = [self.signals]
        elif stage.base_stage.type == StageType.EXTRACT.value:
            self.extracted_signals = feature_extraction(stage.base_stage.subtype, stage.base_stage.config, input_data[0])
            output_data = [self.extracted_signals]
        elif stage.base_stage.type == StageType.INSIGHTS.value:
            self.signals_to_keep, self.signals_to_reduce,  self.text_insights = generate_insights(stage.base_stage.subtype, stage.base_stage.config, input_data[0])
            output_data = [self.signals_to_keep, self.signals_to_reduce,  self.text_insights]
        elif stage.base_stage.type == StageType.CONF_GEN.value:
            self.r_value = config_generator(stage.base_stage.subtype, stage.base_stage.config, input_data[0], input_data[1], input_data[2])
            output_data = [self.r_value]
        elif stage.base_stage.type == StageType.SPLIT.value:
            output_data = split(stage.base_stage.subtype, stage.base_stage.config, input_data[0])
        elif stage.base_stage.type == StageType.MERGE.value:
            self.extracted_signals = merge(stage.base_stage.subtype, stage.base_stage.config, input_data)
            output_data = [self.extracted_signals]
        else:
            raise Exception(f"stage type not implemented: {stage.type}")
        print("run_stage, len of output_data = ", len(output_data))
        stage.set_latest_output_data(output_data)

    def run_multi_stage(self, stage, input_data):
        # make k copies of stage, where k is the number of input lists
        # provide each copy of stage with a single list
        # collect hte output lists into a common output list
        number_of_copies = len(input_data)
        print("run_multi_stage number_of_copies = ", number_of_copies)
        substages = []
        for index in range(number_of_copies):
            stage_copy = copy.copy(stage)
            stage_copy.base_stage.name += f"_{index}"
            stage_copy.base_stage.multi_stage = False
            substages.append(stage_copy)
            new_input_data = [input_data[index]]
            self.run_stage(stage_copy, new_input_data)

        # collect the output data
        output_data = []
        for index in range(number_of_copies):
            output_data.append(substages[index].latest_output_data[0])

        stage.set_latest_output_data(output_data)
        print("end of multi_stage, len of output = ", len(output_data))


    def run_iteration(self):
        for s in self.stage_execution_order:
            print("run_iteration:, s = ", s.base_stage.name)
            if s.base_stage.multi_stage:
                # find the stage where that input field is generated
                i_field = s.base_stage.input_data[0]
                s_prev = self.output_data_dict[i_field]
                input_data = s_prev.latest_output_data
                self.run_multi_stage(s, input_data)
                continue

            if s.base_stage.type == api.StageType.MERGE.value:
                # gather the input data
                i_field = s.base_stage.input_data[0]
                s_prev = self.output_data_dict[i_field]
                input_data = s_prev.latest_output_data
                self.run_stage(s, input_data)
                continue

            # gather the input data
            input_data = []
            for i_field in s.base_stage.input_data:
                # find the stage where that input field is generated
                s_prev = self.output_data_dict[i_field]
                #  latest_output_data contains a list of outputs; select the right one
                for o_field in s_prev.base_stage.output_data:
                    if o_field == i_field:
                        index = s_prev.base_stage.output_data.index(o_field)
                        break
                input_data.append(s_prev.latest_output_data[index])

            self.run_stage(s, input_data)
            print("run_iteration, after run_stage, s = ", s.base_stage.name)


