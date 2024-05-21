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

from common.configuration_api import IngestSubType, ConfigIngestFile, ConfigIngestPromql, ConfigIngestDummy

logger = logging.getLogger(__name__)


def ingest(subtype, config):
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == IngestSubType.INGEST_DUMMY.value:
        logger.debug("using dummy ingest logger")
        ConfigIngestDummy(**config)
        from ingest.dummy_ingest import ingest
        signals = ingest()
    elif subtype == IngestSubType.INGEST_FILE.value:
        # verify config parameters conform to structure
        config1 = ConfigIngestFile(**config)
        from ingest.file_ingest import ingest
        signals = ingest(config1)
    elif subtype == IngestSubType.INGEST_PROMQL.value:
        config1 = ConfigIngestPromql(**config)
        from ingest.promql_ingest import ingest
        signals = ingest(config1)
    else:
        raise "unsupported ingest configuration"
    return signals
