import logging

from common.conf import get_configuration

logger = logging.getLogger(__name__)


def ingest():
    # switch based on the configuration ingest type
    if get_configuration().ingest_type == "dummy":
        logger.debug("using dummy ingest logger")
        from ingest.dummy_ingest import ingest
        signal = ingest()
    elif get_configuration().ingest_type == "file":
        from ingest.file_ingest import ingest
        signal = ingest()
    else:
        raise "unsupported ingest configuration"
    return signal