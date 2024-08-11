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

import json
import logging
import os
import re
from string import Template

from common.signal import Signal, Signals
from common.configuration_api import IngestSubType, IngestFormat, IngestTimeUnit


logger = logging.getLogger(__name__)


def enrich_metric_signature_info(json_signal):
    signature_info = {}
    # first_time and last_time assume that the time-series data is provided in ascending order.
    signature_info["first_time"] = json_signal["values"][0][0]
    signature_info["last_time"] = json_signal["values"][-1][0]
    signature_info["num_of_items"] = len(json_signal["values"])
    signature_info["__name__"] = json_signal["metric"]["__name__"]
    json_signal["metric"]["signature_info"] = signature_info


def ingest(ingest_config):
    signals = Signals()

    signals.metadata["ingest_type"] = IngestSubType.PIPELINE_INGEST_FILE.value
    signals.metadata["ingest_source"] = ingest_config.file_name

    if ingest_config.format == IngestFormat.PIPELINE_INGEST_FORMAT_PROM.value:
        ingest_prometheus_format(ingest_config, signals)
    elif ingest_config.format == IngestFormat.PIPELINE_INGEST_FORMAT_INSTANA_INFRA.value:
        ingest_instana_format(ingest_config, signals)
    elif ingest_config.format == IngestFormat.PIPELINE_INGEST_FORMAT_INSTANA_APP.value:
        ingest_instana_format(ingest_config, signals)
    else:
        raise "unsupported ingest format"

    logger.info(f"number of signals = {len(signals.signals)}")
    signals2 = combine_multiple_metrics_entries(signals)
    logger.info(f"number of combined signals = {len(signals2.signals)}")
    return signals2


def ingest_prometheus_format(ingest_config, signals):
    ingest_file = ingest_config.file_name
    ingest_name_template = ingest_config.ingest_name_template
    ingest_filter_metadata = ingest_config.filter_metadata
    metrics_metadata = []

    logger.info(f"Reading signals from {ingest_file}")
    try:
        with open(ingest_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e

    json_signals = data["data"]["result"]
    for signal_count, json_signal in enumerate(json_signals):
        if 'metric' in json_signal.keys():
            signal_type = "metric"
            enrich_metric_signature_info(json_signal)
            if ingest_name_template != "":
                # adding `count` to allow usage by template
                json_signal["metric"]["count"] = signal_count
                # save original signal name into `original_name` if needed
                if "__name__" in json_signal["metric"]:
                    json_signal["metric"]["original_name"] = json_signal["metric"]["__name__"]
                # build new name based on template
                json_signal["metric"]["__name__"] = Template(
                    ingest_name_template).safe_substitute(json_signal["metric"])
            signal_metadata = json_signal["metric"]
            signal_time_series = json_signal["values"]
            metrics_metadata.append(signal_metadata)

        else:
            raise Exception("Ingest: signal type - Not implemented")

        # filter signals based on ingest_filter_metadata (if exists)
        if ingest_filter_metadata:
            match = re.search(ingest_filter_metadata, str(signal_metadata))
            if match is None:
                continue
        signals.append(Signal(type=signal_type,
                              metadata=signal_metadata,
                              time_series=signal_time_series))
    signals.metadata["metrics_metadata"] = metrics_metadata


def ingest_instana_object(ingest_config, signals, object):
    # object is expected to be of type dict with a field named "metrics", also of type dict
    logger.debug(f"instana ingest config = {ingest_config}")
    multiplier = 1.0
    ingest_name_template = ingest_config.ingest_name_template
    if ingest_config.time_unit == IngestTimeUnit.PIPELINE_TIME_UNIT_MILLISECOND.value:
        multiplier = 0.001
    elif ingest_config.time_unit == IngestTimeUnit.PIPELINE_TIME_UNIT_MICROSECOND.value:
        multiplier = 0.000001
    if 'metrics' in object.keys():
        json_signals = object["metrics"]
        signal_count = 0
        for metric_name, signal_time_series in json_signals.items():
            if len(signal_time_series) == 0:
                continue
            if ingest_config.format == IngestFormat.PIPELINE_INGEST_FORMAT_INSTANA_INFRA.value:
                json_signal = {"metric": {"__name__": metric_name,
                                          "instance": object["host"],
                                          "plugin": object["plugin"],
                                          "label": object["label"],
                                          "snapshotId": object["snapshotId"],
                                          "job": "instana"
                                          },
                               "values": signal_time_series}
            elif ingest_config.format == IngestFormat.PIPELINE_INGEST_FORMAT_INSTANA_APP.value:
                json_signal = {"metric": {"__name__": metric_name,
                                          "id": object["application"]["id"],
                                          "entityType": object["application"]["entityType"],
                                          "label": object["application"]["label"],
                                          "job": "instana"
                                          },
                               "values": signal_time_series}
            else:
                raise Exception("Ingest: signal format not recognized")

            if ingest_name_template != "":
                # adding `count` to allow usage by template
                json_signal["metric"]["count"] = signal_count
                # save original signal name into `original_name` if needed
                if "__name__" in json_signal["metric"]:
                    json_signal["metric"]["original_name"] = json_signal["metric"]["__name__"]
                # build new name based on template
                json_signal["metric"]["__name__"] = Template(
                    ingest_name_template).safe_substitute(json_signal["metric"])
            signal_type = "metric"
            enrich_metric_signature_info(json_signal)
            signal_metadata = json_signal["metric"]
            signal_time_series = json_signal["values"]
            if multiplier != 1.0:
                new_signal_time_series = []
                for timestamp, value in signal_time_series:
                    new_entry = [timestamp*multiplier, value]
                    new_signal_time_series.append(new_entry)
                signal_time_series = new_signal_time_series
            logger.debug(f"adding signal {json_signal['metric']}")
            signals.append(Signal(type=signal_type,
                                  metadata=signal_metadata,
                                  time_series=signal_time_series))
            signal_count += 1
    else:
        raise Exception("Ingest: signal type - Not implemented")


def ingest_instana_helper(ingest_config, signals, list_of_objects):
    for item in list_of_objects:
        if (isinstance(item, list)):
            ingest_instana_helper(ingest_config, signals, item)
        else:
            ingest_instana_object(ingest_config, signals, item)


# combine entries that refer to the same metric
def ingest_instana_format(ingest_config, signals):
    ingest_file = ingest_config.file_name
    logger.info(f"ingesting file {ingest_file}")
    metrics_metadata = []
    if os.path.isfile(ingest_file):
        metrics_metadata = ingest_instana_format_file(ingest_config, signals, ingest_file)
    elif os.path.isdir(ingest_file):
        metrics_metadata = ingest_instana_format_directory(ingest_config, signals, ingest_file)
    else:
        raise "object is neither a directory or a file"

    signals.metadata["metrics_metadata"] = metrics_metadata


def ingest_instana_format_directory(ingest_config, signals, ingest_dir):
    metrics_metadata = []
    for file_name in os.listdir(ingest_dir):
        file_path = os.path.join(ingest_dir, file_name)
        if os.path.isfile(file_path):
            tmp_metrics_metadata = ingest_instana_format_file(ingest_config, signals, file_path)
            metrics_metadata.append(tmp_metrics_metadata)
        elif os.path.isdir(file_path):
            tmp_metrics_metadata = ingest_instana_format_directory(ingest_config, signals, file_path)
            metrics_metadata.append(tmp_metrics_metadata)
        else:
            raise "object is neither a directory or a file"

    return metrics_metadata


def ingest_instana_format_file(ingest_config, signals, ingest_file):
    metrics_metadata = []

    logger.info(f"Reading signals with instana format from {ingest_file}")
    try:
        with open(ingest_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e

    # could have list of list of dict
    ingest_instana_helper(ingest_config, signals, data)

    for signal_count, signal in enumerate(signals.signals):
        metrics_metadata.append(signal.metadata)

    return metrics_metadata


def combine_multiple_metrics_entries(signals):
    signals_dict = {}
    metrics_metadata = []
    merge_performed = False

    for signal in signals.signals:
        signal_name = signal.metadata["__name__"]
        if signal_name in signals_dict:
            merge_performed = True
            signal0 = signals_dict[signal_name]
            new_signals_list = signal0.time_series
            if signal.metadata["signature_info"]["first_time"] < signal0.metadata["signature_info"]["first_time"]:
                signal0.metadata["signature_info"]["first_time"] = signal.metadata["signature_info"]["first_time"]
                new_signals_list = signal.time_series + signal0.time_series
            if signal.metadata["signature_info"]["last_time"] > signal0.metadata["signature_info"]["last_time"]:
                signal0.metadata["signature_info"]["last_time"] = signal.metadata["signature_info"]["last_time"]
                new_signals_list = signal0.time_series + signal.time_series
            signal0.time_series = new_signals_list
            signal0.metadata["signature_info"]["num_of_items"] = len(signal0.time_series)
            # TODO What about other metadata?
            metrics_metadata.append(signal0.metadata)
        else:
            signals_dict[signal_name] = signal

    if not merge_performed:
        return signals

    signals_list = list(signals_dict.values())
    new_signals = Signals(metadata=metrics_metadata, signals=signals_list)
    return new_signals
