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

import copy
import hashlib
import json
import logging
import os
import pickle
import time

import common.configuration_api as api
from common.conf import get_configuration
from multiprocessing import Pool

from config_generator.config_generator import config_generator
from encode.encode import encode
from extract.extract import extract
from ingest.ingest import ingest
from insights.insights import generate_insights
from map_reduce.map import _map
from map_reduce.reduce import reduce
from metadata_classification.metadata_classification import metadata_classification
from workflow_orchestration.map_reduce import MapReduceParameters, create_dummy_compute_stage
from workflow_orchestration.stage import StageParameters


logger = logging.getLogger(__name__)

# TODO: refactor to get rid of this global variable
process_pool = None


class Pipeline:
    def __init__(self):
        self.output_data_dict = {}
        self.stage_execution_order = []
        self.number_of_workers = 0

        # variables used for GUI of POC
        self.signals = None
        self.classified_signals = None
        self.extracted_signals = None
        self.signals_to_keep = None
        self.signals_to_reduce = None
        self.text_insights = None
        self.r_value = None

    def __del__(self):
        global process_pool
        if process_pool is not None:
            process_pool.close()
        process_pool = None

    def build_pipeline(self):
        logger.debug("Building Pipeline")
        stages_params_dict = {}
        stages_pipeline_dict = {}
        configuration = get_configuration()
        pipeline = configuration['pipeline']
        stages_parameters = configuration['parameters']
        map_reduce_stage_exists = False

        # verify that configuration is valid
        # if not valid, the following line will throw an exception
        pipeline_def = api.PipelineDefinition(**configuration)

        # create stage structs for each of the stages
        for stage_params in stages_parameters:
            stg = StageParameters(stage_params)
            if stg.base_stage.name in stages_params_dict:
                raise Exception(
                    f"duplicate stage parameters defined: {stg.base_stage.name}")
            stages_params_dict[stg.base_stage.name] = stg
            if stg.base_stage.type == api.StageType.MAP_REDUCE.value:
                map_reduce_stage_exists = True
        logger.info(f"stages = {stages_params_dict}")

        # Parse pipeline sections to create connections
        # Connects between the stages
        # check that the same stage name does not appear twice in a pipeline
        # section
        for pip_stage in pipeline:
            name = pip_stage['name']
            if name in stages_pipeline_dict:
                raise Exception(
                    f"stage {name} specified more than once in pipeline section")
            stages_pipeline_dict[name] = pip_stage
            if name not in stages_params_dict:
                raise Exception(
                    f"stage {name} not defined in parameters section")
            stg = stages_params_dict[name]
            if 'follows' in pip_stage:
                for follows_stage in pip_stage['follows']:
                    if follows_stage not in stages_params_dict:
                        raise Exception(
                            f"stage {follows_stage} used but not defined")
                    previous_stage = stages_params_dict[follows_stage]
                    stg.set_follows(follows_stage)
                    previous_stage.add_follower(stg)
            else:
                if stg.base_stage.input_data is not None and len(
                        stg.base_stage.input_data) > 0:
                    raise Exception(
                        f"stage {stg.base_stage.name} is a first stage so it should not have input data")

            # collect all the output data items in a dictionary
            for od in stg.base_stage.output_data:
                if od in self.output_data_dict:
                    raise Exception(
                        f"output_data field must be unique to a single stage: {od}")
                self.output_data_dict[od] = stg

        # check that each follows stage actually exists
        for pip_stage in pipeline:
            if 'follows' in pip_stage:
                for follows_stage in pip_stage['follows']:
                    if follows_stage not in stages_pipeline_dict:
                        raise Exception(
                            f"stage {follows_stage} used but not declared in pipeline section")

        # decide the order in which to run the stages
        # TBD - eventually support parallel execution of tasks of DAG
        # for now, run the tasks serially. determine a legal order.
        for stage in stages_params_dict.values():
            self.add_stage_to_schedule(stage)

        global_settings = api.GlobalSettings(**pipeline_def.global_settings)

        # allocate process pool for map_reduce
        number_of_workers = global_settings.number_of_workers
        logger.info(f"number_of_workers =  {number_of_workers}")
        if map_reduce_stage_exists and number_of_workers > 0:
            global process_pool
            process_pool = Pool(processes=number_of_workers)

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

    def run_stage_wrapper(self, args):
        output_data = run_stage(args)
        stage = args[0]

        if stage.base_stage.type == api.StageType.INGEST.value:
            self.signals = output_data[0]
            if stage.base_stage.subtype == api.IngestSubType.PIPELINE_INGEST_SERIALIZED.value:
                self.extracted_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.METADATA_CLASSIFICATION.value:
            self.classified_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.EXTRACT.value:
            self.extracted_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.INSIGHTS.value:
            self.signals_to_keep, self.signals_to_reduce, self.text_insights = (
                output_data[0], output_data[1], output_data[2])
        elif stage.base_stage.type == api.StageType.CONFIG_GENERATOR.value:
            self.r_value = output_data[0]
        elif stage.base_stage.type == api.StageType.MAP_REDUCE.value:
            self.extracted_signals = output_data[0]
        elif stage.base_stage.type == api.StageType.ENCODE.value:
            # do nothing
            pass
        else:
            raise Exception(f"stage type not implemented: {stage.type}")
        stage.set_latest_output_data(output_data)
        return output_data

    def run_iteration(self):
        for current_stage in self.stage_execution_order:
            # gather the input data
            input_data = []
            for input_field in current_stage.base_stage.input_data:
                # find the stage where that input field is generated
                previous_stage = self.output_data_dict[input_field]
                # latest_output_data contains a list of outputs; select the
                # right one
                for output_field in previous_stage.base_stage.output_data:
                    if output_field == input_field:
                        index = previous_stage.base_stage.output_data.index(
                            output_field)
                        break
                input_data.append(previous_stage.latest_output_data[index])

            args = [current_stage, input_data]
            self.run_stage_wrapper(args)


def map_reduce(config, input_data):
    # verify config parameters structure
    logger.debug("running map_reduce")
    params = MapReduceParameters(**config)
    logger.debug("before map")
    input_lists = _map(params.map_function.subtype,
                       params.map_function.config, input_data)
    logger.debug("after map")
    dummy_stage = create_dummy_compute_stage(params.compute_function)
    logger.debug(f"dummy stage: {dummy_stage}")
    logger.debug("**************** before run_map_reduce_compute")
    output_lists = run_map_reduce_compute(dummy_stage, input_lists)
    logger.debug("**************** after run_map_reduce_compute")
    logger.debug("before reduce")
    output_data = reduce(params.reduce_function.subtype,
                         params.reduce_function.config, output_lists)
    logger.debug("after reduce")
    return output_data


def run_map_reduce_compute(stage, input_data):
    # make k copies of stage, where k is the number of input lists
    # provide each copy of stage with a single list
    # collect the output lists into a common output list
    # we run each copy of stage in a separate thread.
    # if we have a pool of processes, we run each copy of stage on the pool of processes
    number_of_copies = len(input_data)
    logger.debug(f"************************ run_map_reduce_compute: stage = {stage}")
    logger.info(f"Executing map-reduce on stage = {stage} . Mapping into {number_of_copies} stages")
    sub_stages = []
    run_stage_args = []
    for index in range(number_of_copies):
        logger.debug(f"stage name = {stage.base_stage.name}")
        stage_copy = copy.deepcopy(stage)
        stage_copy.base_stage.name += f"_{index}"
        logger.info(f"=== #{index} ===> executing parallel stage {stage_copy.base_stage.name}")
        sub_stages.append(stage_copy)
        new_input_data = [input_data[index]]
        args = [stage_copy, new_input_data]
        run_stage_args.append(args)

    if process_pool is not None:
        logger.info("************************ running map/reduce using pool of processes ")
        output_data = process_pool.map(run_stage, run_stage_args)
        logger.debug(f"output_data = {output_data}")
        stage.set_latest_output_data(output_data)
        logger.info(f"************************ exiting run_map_reduce_compute: stage = {stage.base_stage.name}")
        return output_data

    # continue here if not using workers processes
    # should use threads, but they don't run in parallel because of Global Lock
    logger.debug("************************ running without worker processes ")
    for index in range(number_of_copies):
        run_stage(run_stage_args[index])

    # collect the output data
    output_data = []
    for index in range(number_of_copies):
        output_data.append(sub_stages[index].latest_output_data)

    stage.set_latest_output_data(output_data)
    logger.info("Done. (Executing map-reduce)")
    return output_data


def hash_metadata(metadata):
    logger.debug(f"metadata = {metadata}")
    json_string = json.dumps(metadata, sort_keys=True).encode()
    hash_value = hashlib.sha1(json_string).hexdigest()
    logger.debug(f"hash_value = {hash_value}")
    logger.debug(f"json_string = {json_string}")
    return hash_value, json_string


def search_cache_directory(stage, signals_in):
    hash_value, json_string = hash_metadata(signals_in.metadata["metrics_metadata"])
    path = stage.base_stage.cache_directory + '/' + hash_value
    signals_file = path + '/' + 'signals_file'
    logger.info(f"in stage {stage.base_stage.name} reading data from {signals_file}")
    try:
        with open(signals_file, 'rb') as file:
            data = pickle.load(file)
            return True, data
    except Exception as e:
        logger.info(f"Error reading data from {path}: {e}")
        return False, []


def cache_output_data(cache_directory, signals_in, signals_out):
    metrics_metadata = signals_in.metadata["metrics_metadata"]
    hash_value, json_string = hash_metadata(metrics_metadata)
    path = cache_directory + '/' + hash_value
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"created cache directory {path}")
    except Exception as e:
        err = f"Error creating directory {path}: {e}"
        raise RuntimeError(err) from e
    metadata_file = path + '/' + 'metadata_file'
    signals_file = path + '/' + 'signals_file'
    try:
        with open(metadata_file, 'wb') as file:
            file.write(json_string)
    except Exception as e:
        err = f"Error on file {metadata_file}: {e}"
        raise RuntimeError(err) from e
    try:
        with open(signals_file, 'wb') as file:
            pickle.dump(signals_out, file)
    except Exception as e:
        err = f"Error on file {signals_file}: {e}"
        raise RuntimeError(err) from e

    return


def run_stage(args):
    stage = args[0]
    input_data = args[1]
    if stage.base_stage.cache_directory is not None:
        # if input data is found in cache, return the results directly from the cache directory
        # TODO: verify types before operating on them
        # verify that input consists of single element from which we make the hash
        signals_in = input_data[0]
        if len(input_data) == 1:
            found, signals_out = search_cache_directory(stage, signals_in)
            if found:
                return signals_out
    logger.info(f"running stage: {stage.base_stage.name}, len(input_data) = {len(input_data)}")
    start_time = time.time()
    logger.debug(f"stage = {stage}, input = {input_data}")
    if stage.base_stage.type == api.StageType.INGEST.value:
        output_data = ingest(stage.base_stage.subtype, stage.base_stage.config)
    elif stage.base_stage.type == api.StageType.METADATA_CLASSIFICATION.value:
        output_data = metadata_classification(stage.base_stage.subtype, stage.base_stage.config, input_data)
    elif stage.base_stage.type == api.StageType.EXTRACT.value:
        output_data = extract(stage.base_stage.subtype, stage.base_stage.config, input_data)
    elif stage.base_stage.type == api.StageType.INSIGHTS.value:
        output_data = generate_insights(stage.base_stage.subtype, stage.base_stage.config, input_data)
    elif stage.base_stage.type == api.StageType.CONFIG_GENERATOR.value:
        output_data = config_generator(stage.base_stage.subtype, stage.base_stage.config, input_data)
    elif stage.base_stage.type == api.StageType.MAP_REDUCE.value:
        output_data = map_reduce(stage.base_stage.config, input_data)
    elif stage.base_stage.type == api.StageType.ENCODE.value:
        output_data = encode(stage.base_stage.subtype, stage.base_stage.config, input_data)
    else:
        raise Exception(f"stage type not implemented: {stage.base_stage.type}")
    stage.set_latest_output_data(output_data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"finished stage: {stage.base_stage.name}; elapsed time = {elapsed_time}")
    if stage.base_stage.cache_directory is not None:
        # save data in cache directory
        cache_output_data(stage.base_stage.cache_directory, input_data[0], output_data)
    return output_data
