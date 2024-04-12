import logging
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


if __name__ == '__main__':
    main()
