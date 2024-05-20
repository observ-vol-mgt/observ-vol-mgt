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

import logging

from common.configuration_api import TYPE_INGEST_CLUSTERING, SUBTYPE_INGEST_CLUSTERING_BY_NAME

logger = logging.getLogger(__name__)


def ingest_clustering(subtype, config, signals):
    # switch based on the configuration ingest type
    if subtype == SUBTYPE_INGEST_CLUSTERING_BY_NAME:
        logger.debug("using by_name ingest clustering")
        from ingest_clustering.by_name_ingest_clustering import ingest_clustering
        clustered_signals = ingest_clustering(config, signals)
    else:
        raise "unsupported ingest_clustering sub_type"
    return clustered_signals
