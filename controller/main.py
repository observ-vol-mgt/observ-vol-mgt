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

from common.conf import parse_args
from common.conf import get_args
from workflow_orchestration.pipeline import Pipeline
from ui.visualization import flaskApp, fill_time_series, fill_insights

logger = logging.getLogger(__name__)


def main():
    # getting the configuration
    parse_args()
    pipeline = Pipeline()
    pipeline.build_pipeline()

    # set log level
    level = logging.getLevelName(get_args().loglevel.upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # starting the pipeline
    logger.info("Starting the Controller Pipeline")
    logger.info("--=-==--=-==--=-==--=-=-=-=-==--")
    pipeline.run_iteration()

    logger.info(f"the ingested signals are: {pipeline.signals}")
    logger.info(f"the feature_extracted signals are: {pipeline.extracted_signals}")

    logger.info(f"the insights are: {pipeline.text_insights}")
    logger.info(f"Config Generator returned: {pipeline.r_value}")

    # Show the UI
    logger.info(f"To Visualize the signals use the provided URL:")
    fill_time_series(pipeline.extracted_signals)
    fill_insights(pipeline.text_insights)

    flaskApp.run(debug=False)


if __name__ == '__main__':
    main()
