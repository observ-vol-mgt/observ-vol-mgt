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
from common.conf import get_first_stage
from common.conf import parse_args
from common.conf import get_args
from config_generator.config_generator import config_generator
from feature_extraction.feature_extraction import feature_extraction
from ingest.ingest import ingest
from insights.insights import generate_insights
from ui.visualization import flaskApp, fill_time_series, fill_insights


logger = logging.getLogger(__name__)

signals = None
extracted_signals = None
signals_to_keep = None
signals_to_reduce = None
text_insights = None

def run_stage(stage, input_data):
    print("stage = ", stage.name)
    attrs = vars(stage)
    print(', '.join("%s: %s" % item for item in attrs.items()))
    if stage.type == 'ingest':
        global signals
        signals = ingest(stage)
        output_data = [signals]
    elif stage.type == 'extract':
        global extracted_signals
        extracted_signals = feature_extraction(stage, input_data)
        output_data = [extracted_signals]
    elif stage.type == 'insights':
        global signals_to_keep, signals_to_reduce, text_insights
        signals_to_keep, signals_to_reduce,  text_insights = generate_insights(stage, input_data)
        output_data = [signals_to_keep, signals_to_reduce,  text_insights]
    else:
        str = "stage type not implemented: " + stage.type
        raise str
    for s in stage.followers:
        run_stage(s, output_data)

def main():
    # getting the configuration
    parse_args()

    # set log level
    level = logging.getLevelName(get_args().loglevel.upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # starting the pipeline
    logger.info("Starting the Controller Pipeline")
    logger.info("--=-==--=-==--=-==--=-=-=-=-==--")
    run_stage(get_first_stage(), [])

    logger.info(f"the ingested signals are: {signals}")
    logger.info(f"the feature_extracted signals are: {extracted_signals}")

    logger.info(f"the insights are: {text_insights}")
    r_value = config_generator(extracted_signals, signals_to_keep, signals_to_reduce)
    logger.info(f"Config Generator returned: {r_value}")

    # Show the UI
    logger.info(f"To Visualize the signals use the provided URL:")
    fill_time_series(extracted_signals)
    fill_insights(text_insights)

    flaskApp.run(debug=False)


if __name__ == '__main__':
    main()
