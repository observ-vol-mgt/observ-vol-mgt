from flask import Flask, jsonify, request, abort
from flask_swagger_ui import get_swaggerui_blueprint
from config import *
import requests
import logging
import yaml
import os

app = Flask(__name__)
SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"
HOST=os.environ.get('HOST')
PORT=os.environ.get('PORT')
RULES_FOLDER=os.environ.get('RULES_FOLDER')
THANOS_RULE_URL=os.environ.get('THANOS_RULE_URL')
LOG_FILE=os.environ.get('LOG_FILE')

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Thanos Ruler API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

log_dir = os.path.dirname(f'{LOG_FILE}')
logging.basicConfig(filename=f'{LOG_FILE}', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/<rule_id>', methods=['POST'])
def create_rule(rule_id):
    logger.debug(f"ADD alert rule {rule_id}")
    try:
        rule_data = request.get_data()
        try:
            r_data = yaml.safe_load(rule_data)
        except Exception as e:
            logger.error("Invalid yaml data")
            return {"message":"Invalid YAML data"}, 400
        description = r_data.get('description')
        if 'description' not in r_data.keys():
            description = r_data.get('expr')
        #TODO: check if rule_id already exists
        
        new_yaml_data_dict = {
            'alert': f'{rule_id}',
            'annotations': {'description': description,
                'summary': 'Usage {{ $labels.label_0 }} of tenant {{ $labels.tenant_id }} is above 100.',
            },
            'expr': r_data.get('expr'),
            'for': r_data.get('for'),
            'labels': {'severity': 'critical'},
        }
        file_path = os.path.join(f"{RULES_FOLDER}", f"rules.yml")
        with open(file_path,'r') as yamlfile:
            exists = False
            cur_yaml = yaml.safe_load(yamlfile)
            for index in range(len(cur_yaml["groups"][0]["rules"])):
                if cur_yaml["groups"][0]["rules"][index]["alert"] == f'{rule_id}':
                    cur_yaml["groups"][0]["rules"][index] = new_yaml_data_dict
                    exists = True
                    break
            if exists != True:    
                if not cur_yaml["groups"][0]["rules"]:
                    cur_yaml["groups"][0]["rules"] = []
                cur_yaml["groups"][0]["rules"].append(new_yaml_data_dict)
        if cur_yaml:
            with open(file_path,'w') as yamlfile:
                yaml.safe_dump(cur_yaml, yamlfile, default_flow_style=False, sort_keys=False) 
        url = THANOS_RULE_URL + "/-/reload"
        r = requests.post(url)
        logger.info(f"POST request successful for rules")
        return {"message":"success"}, 200

    except Exception as e:
        logger.error(f"Error occurred while creating rule: {str(e)}")
        abort(500, "An error occurred while creating the rule")

@app.route('/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    logger.debug(f"DELETE alert rule {rule_id}")
    try:
        file_path = os.path.join(f"{RULES_FOLDER}", f"rules.yml")
        with open(file_path,'r') as yamlfile:
                cur_yaml = yaml.safe_load(yamlfile)
        for alert in cur_yaml["groups"][0]["rules"]:
                if alert.get("alert") == f'{rule_id}':
                    cur_yaml["groups"][0]["rules"].remove(alert)
                    with open(file_path,'w') as yamlfile:
                        yaml.safe_dump(cur_yaml, yamlfile, default_flow_style=False, sort_keys=False)
                    url = THANOS_RULE_URL + "/-/reload"
                    r = requests.post(url)
                    logger.info(f"DELETE request successful for rules")
                    return {"message":"success"}, 200  
        return {"message":"success"}, 200
    except Exception as e:
        logger.error(f"Error occurred while deleting rule: {str(e)}")
        abort(500, "An error occurred while deleting the rule")

@app.route('/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    logger.debug(f"GET alert rule {rule_id}")
    try:
        file_path = os.path.join(f"{RULES_FOLDER}", f"rules.yml")
        with open(file_path,'r') as yamlfile:
                cur_yaml = yaml.safe_load(yamlfile)
        for alert in cur_yaml["groups"][0]["rules"]:
                if alert.get("alert") == f'{rule_id}':
                    logger.info(f"GET request successful for the rule {rule_id}")
                    return jsonify(alert), 200
        return {"message":"rule not found"}, 200
    except Exception as e:
        logger.error(f"Error occurred while getting rule: {str(e)}")
        abort(500, "An error occurred while getting the rule")

@app.route('/rules', methods=['GET'])
def get_all_rules():
    try:
        rule_list = []
        file_path = os.path.join(f"{RULES_FOLDER}", f"rules.yml")
        with open(file_path,'r') as yamlfile:
                cur_yaml = yaml.safe_load(yamlfile) # Note the safe_load
        for alert in cur_yaml["groups"][0]["rules"]:
             rule_list.append(alert)
        logger.debug(f"GET all rules successful")
        return jsonify(rule_list), 200
    except Exception as e:
        logger.error(f"Error occurred while fetching rules: {str(e)}")
        abort(500, "An error occurred while fetching the rules")
if __name__ == '__main__':
    app.run(host=f"{HOST}", port=f"{PORT}", debug=True)
