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

import common.configuration_api as api

logger = logging.getLogger(__name__)


def ingest(subtype, config):
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.IngestSubType.PIPELINE_INGEST_DUMMY.value:
        logger.debug("using dummy ingest logger")
        api.IngestDummy(**config)
        from ingest.dummy_ingest import ingest
        signals = ingest()
    elif subtype == api.IngestSubType.PIPELINE_INGEST_FILE.value:
        # verify config parameters conform to structure
        typed_config = api.IngestFile(**config)
        from ingest.file_ingest import ingest
        signals = ingest(typed_config)
    elif subtype == api.IngestSubType.PIPELINE_INGEST_SERIALIZED.value:
        # verify config parameters conform to structure
        typed_config = api.IngestSerialized(**config)
        from ingest.pickle_ingest import ingest
        signals = ingest(typed_config)
    elif subtype == api.IngestSubType.PIPELINE_INGEST_PROMQL.value:
        typed_config = api.IngestPromql(**config)
        from ingest.promql_ingest import ingest
        signals = ingest(typed_config)
    else:
        raise "unsupported ingest configuration"
    return [signals]
