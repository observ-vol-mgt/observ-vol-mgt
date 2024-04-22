from flask import Flask
import processor
import rules
import alerthandler
import logging
from config import *
import os


app = Flask(__name__)

# Set up logging
log_dir = os.path.dirname(LOG_FILE)
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=LOG_FILE, filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.register_blueprint(processor.processor_bp, url_prefix=APP_URL_PREFIX)
    app.register_blueprint(rules.rules_bp, url_prefix=APP_URL_PREFIX)
    app.register_blueprint(alerthandler.alerthandler_bp)
    app.run(host=HOST, port=PORT, debug=True)
    logger.info('Manager started successfully.')

