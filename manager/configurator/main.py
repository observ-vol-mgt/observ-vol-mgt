from flask import Flask
import processors
import rules
import alerthandler
import logging
import os
import yaml


app = Flask(__name__)

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    app.config.update(load_config(config_file))

# Set up logging
log_dir = os.path.dirname(app.config.get('LOG_FILE'))
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=app.config.get('LOG_FILE'), filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app.register_blueprint(processors.processor_bp, url_prefix=app.config.get('APP_URL_PREFIX'))
    app.register_blueprint(rules.rules_bp, url_prefix=app.config.get('APP_URL_PREFIX'))
    app.register_blueprint(alerthandler.alerthandler_bp)
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=True)
    logger.info('Manager started successfully.')
