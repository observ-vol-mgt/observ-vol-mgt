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
from metadata_classification.metadata_classification import metadata_classification
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights
from common.configuration_api import StageType

import logging

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        self.output_data_dict = {}
        self.stage_execution_order = []

        # variables used for GUI of POC
        self.signals = None
        self.classified_signals = None
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

        # Parse pipeline sections to create connections
        # Connects between the stages
        # check that the same stage name does not appear twice in a pipeline section
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

        # decide the order in which to run the stages
        # TBD - eventually support parallel execution of tasks of DAG
        # for now, run the tasks serially. determine a legal order.
        for stage in stages_params_dict.values():
            self.add_stage_to_schedule(stage)

    def add_stage_to_schedule(self, s):
        if s.scheduled:
            return
        for i in s.base_stage.input_data:
            s_prev = self.output_data_dict[i]
            if not s_prev.scheduled:
                self.add_stage_to_schedule(s_prev)
        self.stage_execution_order.append(s)
        s.set_scheduled()

    def run_stage(self, stage, input_data):
        if stage.base_stage.type == StageType.INGEST.value:
            output_data = ingest(stage.base_stage.subtype, stage.base_stage.config)
            self.signals = output_data[0]
        elif stage.base_stage.type == StageType.METADATA_CLASSIFICATION.value:
            output_data = metadata_classification(stage.base_stage.subtype, stage.base_stage.config,
                                                              input_data)
            self.classified_signals = output_data[0]
        elif stage.base_stage.type == StageType.METADATA_EXTRACTION.value:
            output_data = feature_extraction(stage.base_stage.subtype, stage.base_stage.config,
                                                        input_data)
            self.extracted_signals = output_data[0]
        elif stage.base_stage.type == StageType.INSIGHTS.value:
            output_data = generate_insights(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.signals_to_keep, self.signals_to_reduce, self.text_insights = output_data[0], output_data[1], output_data[2]
        elif stage.base_stage.type == StageType.CONFIG_GENERATOR.value:
            output_data = config_generator(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.r_value = output_data[0]
        else:
            raise Exception(f"stage type not implemented: {stage.type}")
        stage.set_latest_output_data(output_data)

    def run_iteration(self):
        for s in self.stage_execution_order:
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
