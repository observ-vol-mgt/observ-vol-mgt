import logging
from ingest.ingest import ingest
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
    signal = ingest()
    logger.info(f"the ingested signal is: {signal}")


if __name__ == '__main__':
    main()
