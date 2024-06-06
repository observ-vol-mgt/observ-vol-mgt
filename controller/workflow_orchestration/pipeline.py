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
from workflow_orchestration.map_reduce import MapReduceParameters, create_dummy_compute_stage

from config_generator.config_generator import config_generator
from metadata_classification.metadata_classification import metadata_classification
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights
import common.configuration_api as api
from map_reduce.map import map
from map_reduce.reduce import reduce

import logging
import copy
import threading

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
        logger.debug("Building Pipeline")
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
                raise Exception(f"stage {name} not defined in parameters section")
            stg = stages_params_dict[name]
            if 'follows' in pip_stage:
                for follows_stage in pip_stage['follows']:
                    if follows_stage not in stages_params_dict:
                        raise Exception(f"stage {follows_stage} used but not defined")
                    previous_stage = stages_params_dict[follows_stage]
                    stg.set_follows(follows_stage)
                    previous_stage.add_follower(stg)
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
                for follows_stage in pip_stage['follows']:
                    if follows_stage not in stages_pipeline_dict:
                        raise Exception(f"stage {follows_stage} used but not declared in pipeline section")

        # decide the order in which to run the stages
        # TBD - eventually support parallel execution of tasks of DAG
        # for now, run the tasks serially. determine a legal order.
        for stage in stages_params_dict.values():
            self.add_stage_to_schedule(stage)

    def add_stage_to_schedule(self, current_stage):
        logger.debug(f"adding stage = {current_stage} to schedule")
        if current_stage.scheduled:
            return
        for input_field in current_stage.base_stage.input_data:
            previous_stage = self.output_data_dict[input_field]
            if not previous_stage.scheduled:
                self.add_stage_to_schedule(previous_stage)
        self.stage_execution_order.append(current_stage)
        current_stage.set_scheduled()

    def run_stage(self, stage, input_data):
        logger.debug(f"running stage: {stage}")
        if stage.base_stage.type == api.StageType.INGEST.value:
            output_data = ingest(stage.base_stage.subtype, stage.base_stage.config)
            self.signals = output_data[0]
        elif stage.base_stage.type == api.StageType.METADATA_CLASSIFICATION.value:
            output_data = metadata_classification(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.classified_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.METADATA_EXTRACTION.value:
            output_data = feature_extraction(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.extracted_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.INSIGHTS.value:
            output_data = generate_insights(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.signals_to_keep, self.signals_to_reduce, self.text_insights = output_data[0], output_data[1], output_data[2]
        elif stage.base_stage.type == api.StageType.CONFIG_GENERATOR.value:
            output_data = config_generator(stage.base_stage.subtype, stage.base_stage.config, input_data)
            self.r_value = output_data[0]
        elif stage.base_stage.type == api.StageType.MAP_REDUCE.value:
            output_data = self.map_reduce(stage.base_stage.config, input_data)
            self.extracted_signals = output_data[0]
        else:
            raise Exception(f"stage type not implemented: {stage.type}")
        stage.set_latest_output_data(output_data)

    def run_iteration(self):
        for current_stage in self.stage_execution_order:
            # gather the input data
            input_data = []
            for input_field in current_stage.base_stage.input_data:
                # find the stage where that input field is generated
                previous_stage = self.output_data_dict[input_field]
                #  latest_output_data contains a list of outputs; select the right one
                for output_field in previous_stage.base_stage.output_data:
                    if output_field == input_field:
                        index = previous_stage.base_stage.output_data.index(output_field)
                        break
                input_data.append(previous_stage.latest_output_data[index])
            self.run_stage(current_stage, input_data)


    def map_reduce(self, config, input_data):
        # verify config parameters structure
        logger.debug(f"running map_reduce")
        params = MapReduceParameters(**config)
        logger.debug(f"before map")
        input_lists = map(params.map_function.subtype, params.map_function.config, input_data)
        logger.debug(f"after map")
        dummy_stage = create_dummy_compute_stage(params.compute_function)
        logger.debug(f"dummy stage: {dummy_stage}")
        output_lists = self.run_map_reduce_compute(dummy_stage, input_lists)
        logger.debug(f"before reduce")
        output_data = reduce(params.reduce_function.subtype, params.reduce_function.config, output_lists)
        logger.debug(f"after reduce")
        return output_data


    def run_map_reduce_compute(self, stage, input_data):
        # make k copies of stage, where k is the number of input lists
        # provide each copy of stage with a single list
        # collect the output lists into a common output list
        # we run each copy of stage in a separate thread.
        number_of_copies = len(input_data)
        logger.info(f"************************ run_map_reduce_compute: stage = {stage}")
        substages = []
        threads_list = []
        logger.info(f"************************ number of parallel items in mapreduce = {number_of_copies}")
        for index in range(number_of_copies):
            logger.debug(f"stage name = {stage.base_stage.name}")
            stage_copy = copy.deepcopy(stage)
            stage_copy.base_stage.name += f"_{index}"
            logger.debug(f"************************ parallel stage name = {stage_copy.base_stage.name}")
            substages.append(stage_copy)
            new_input_data = [input_data[index]]
            new_thread = threading.Thread(target=self.run_stage, args=(stage_copy, new_input_data))
            threads_list.append(new_thread)
            new_thread.start()

        # wait for the threads to complete
        for index in range(number_of_copies):
            logger.info(f"************************ waiting for thread {index}")
            threads_list[index].join()

        logger.info("************************ finished waiting for threads")

        # collect the output data
        output_data = []
        for index in range(number_of_copies):
            output_data.append(substages[index].latest_output_data[0])

        stage.set_latest_output_data(output_data)
        return output_data

