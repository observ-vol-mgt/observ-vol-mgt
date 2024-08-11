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

from common.conf import parse_args, get_args
from ux.api import _rerun
from workflow_orchestration.pipeline import Pipeline
from ux.ux import start_ux

logger = logging.getLogger(__name__)


def run():
    # Getting configuration
    parse_args()
    _pipeline = Pipeline()
    _pipeline.build_pipeline()

    # Setting log level
    level = logging.getLevelName(get_args().loglevel.upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # Executing the first iteration of the pipline
    if get_args().noui:
        _rerun()


if __name__ == '__main__':
    run()
    # starting the UX (UI and API)
    if not get_args().noui:
        start_ux()
