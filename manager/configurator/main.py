from flask import Flask
from flasgger import Swagger
import processors
import rules
import controller
import alerthandler
import logging
import os
import yaml
from models.ProcessorsConfig import ProcessorsConfig
from models.schemas import schemas

app = Flask(__name__)

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    app.config.update(load_config(config_file))

# Set up logging
try:
    log_dir = os.path.dirname(app.config.get('LOG_FILE'))
    if log_dir != "":
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=app.config.get('LOG_FILE'), filemode='w', level=logging.INFO)
except Exception as e:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Manager API",
        "version": "1.0",
        "description": "API to interact with the Manager"
    },
    "paths": {},
    "components": {
        'schemas': schemas
    }
}


if __name__ == '__main__':
    app.register_blueprint(processors.processor_bp, url_prefix=app.config.get('APP_URL_PREFIX'))
    app.register_blueprint(rules.rules_bp, url_prefix=app.config.get('APP_URL_PREFIX'))
    app.register_blueprint(controller.controller_bp, url_prefix=app.config.get('APP_URL_PREFIX'))
    app.register_blueprint(alerthandler.alerthandler_bp)


    #Swagger(app)
    Swagger(app, template=swagger_template)

    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'), debug=True)
    logger.info('Manager started successfully.')
