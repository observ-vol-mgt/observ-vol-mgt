import logging
from common.conf import get_configuration

logger = logging.getLogger(__name__)


def feature_extraction(signals):
    # switch based on the configuration feature_extraction type
    if get_configuration().feature_extraction_type == "tsfel":
        logger.info("using tsfel feature_extraction")
        from feature_extraction.feature_extraction_tsfel import extract
        extracted_signals = extract(signals)
    elif get_configuration().ingest_type == "tsfresh":
        logger.info("using tsfresh feature_extraction")
        from feature_extraction.feature_extraction_tsfresh import extract
        extracted_signals = extract(signals)
    else:
        raise "unsupported ingest configuration"
    return extracted_signals
