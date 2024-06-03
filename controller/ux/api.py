#   Copyright 2024 IBM, Inc.
#  #
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  #
#       http://www.apache.org/licenses/LICENSE-2.0
#  #
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import os

from flask import Blueprint
from controller.ux.utils import fill_time_series, fill_insights
from controller.workflow_orchestration.pipeline import Pipeline

logger = logging.getLogger(__name__)

api_prefix = "/api/v1/"

current_path = os.path.dirname(os.path.realpath(__file__))
api = Blueprint('api', __name__,
                template_folder=current_path,
                static_folder=f"{current_path}/static")


@api.route(f'{api_prefix}rerun', methods=['POST', 'GET'])
def _rerun():
    """
    Rerun the pipeline
    ---
    responses:
      200:
        description: Success
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """
    try:
        # Build a new pipline
        _pipeline = Pipeline()
        _pipeline.build_pipeline()

        # Execute the pipeline
        logger.debug("Starting Pipeline iteration")
        logger.debug("--=-==--=-==--=-==--=-=-=-=-==--")
        _pipeline.run_iteration()
        logger.debug("Pipeline iteration completed")

        logger.debug(f"the ingested signals are: {_pipeline.signals}")
        logger.debug(f"the feature_extracted signals are: {_pipeline.extracted_signals}")

        logger.debug(f"the insights are: {_pipeline.text_insights}")
        logger.debug(f"Config Generator returned: {_pipeline.r_value}")

        fill_time_series(_pipeline.extracted_signals)
        fill_insights(_pipeline.text_insights)

    except Exception as e:
        return str(e), 500

    return "success"
