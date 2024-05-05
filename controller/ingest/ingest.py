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

from common.conf import get_configuration

logger = logging.getLogger(__name__)


def ingest():
    # switch based on the configuration ingest type
    if get_configuration().ingest_type == "dummy":
        logger.debug("using dummy ingest logger")
        from ingest.dummy_ingest import ingest
        signals = ingest()
    elif get_configuration().ingest_type == "file":
        from ingest.file_ingest import ingest
        signals = ingest()
    elif get_configuration().ingest_type == "promql":
        from ingest.promql_ingest import ingest
        signals = ingest()
    else:
        raise "unsupported ingest configuration"
    return signals
