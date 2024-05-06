HOST = '0.0.0.0'
PORT = 5010
APP_URL_PREFIX = "/api/v1"
LOG_FILE = "./app/logs/manager.log"

PROCESSORS_FOLDER = "./app/processors"
RULES_FOLDER = "./app/rules"

PROCESSOR_1_URL = "http://pmf_processor:8100/morphchain/create"
PROCESSOR_2_URL = "http://pmf_processor:8100/morphchain/create"

ALERTMANAGER_URL = "http://ruler_config:8090"
