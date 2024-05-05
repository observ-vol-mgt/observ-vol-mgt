import logging

from config_generator.config_generator import config_generator
from insights.insights import generate_insights
from ui.visualization import flaskApp, fill_time_series, fill_insights
from ingest.ingest import ingest
from feature_extraction.feature_extraction import feature_extraction
from common.conf import parse_configuration
from common.conf import get_configuration

logger = logging.getLogger(__name__)


def main():
    # getting the configuration
    parse_configuration()

    # set log level
    level = logging.getLevelName(get_configuration().loglevel.upper())
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

    # starting the pipeline
    logger.info("Starting the Controller Pipeline")
    logger.info("--=-==--=-==--=-==--=-=-=-=-==--")
    signals = ingest()
    logger.info(f"the ingested signals are: {signals}")
    extracted_signals = feature_extraction(signals)
    logger.info(f"the feature_extracted signals are: {extracted_signals}")
    signals_to_keep, signals_to_reduce, text_insights = generate_insights(extracted_signals)
    logger.info(f"the insights are: {text_insights}")
    r_value = config_generator(signals_to_keep, signals_to_reduce)
    logger.info(f"Config Generator returned: {r_value}")

    # Show the UI
    logger.info(f"To Visualize the signals use the provided URL:")
    fill_time_series(extracted_signals)
    fill_insights(text_insights)

    flaskApp.run(debug=False)


if __name__ == '__main__':
    main()
