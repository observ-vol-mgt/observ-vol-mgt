from config import *
from flask import Flask, jsonify, request, Blueprint
import logging
import os
import yaml
import json

from models.Rules import Rules
from utils.file_ops.rules import *
from utils.communication import alertmanager
from pydantic import ValidationError


rules_bp = Blueprint('rules', __name__)
logger = logging.getLogger(__name__)

rules_bp.config = {}

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_file = os.environ.get('CONFIG_FILE')
if config_file:
    rules_bp.config.update(load_config(config_file))

RULES_FOLDER = rules_bp.config['RULES_FOLDER']
ALERTMANAGER_URL = rules_bp.config['ALERTMANAGER_URL']

os.makedirs(RULES_FOLDER, exist_ok=True)
rule_ids = load_rules(RULES_FOLDER)

@rules_bp.route('/rules', methods=['POST'])
def update_rules():
    """
    Update rules by creating or replacing them
    ---
    tags:
      - Rules
    operationId: updateRules
    parameters:
      - name: rules_data
        in: body
        description: YAML data containing rules to be created or replaced
        required: true
        content:
          application/yaml:
            schema:
              $ref: '#/components/schemas/Rules'
    responses:
      201:
        description: Successfully created or replaced rules
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                successfully_created:
                  type: array
                  items:
                    type: string
      400:
        description: Invalid YAML data
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                error:
                  type: string
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                successfully_created:
                  type: array
                  items:
                    type: string
    """
    logger.debug("Rules create and/or replace request received")
    success_list = []
    try:
        rules_data = request.get_data(as_text=True)
        # Validate if the provided data is valid YAML
        try:
            rules_data_yaml = yaml.safe_load(rules_data)
            if "rules" not in rules_data_yaml:
                return jsonify({"message" : "Invalid YAML data"}), 400
            rules_data_yaml_validated = Rules(rules=rules_data_yaml["rules"])
        except ValidationError as e:
            return jsonify({"message" : "Invalid YAML data", "error": e.errors()}), 400
        except Exception as e:
            return jsonify({"message" : "Error validating YAML data", "error": str(e)}), 500

        for rule in rules_data_yaml['rules']:
            rule_id = rule["rule_id"]
            response = alertmanager.add_rule(rule, ALERTMANAGER_URL)
            status_code = response.status_code
            if status_code not in [200, 201]:
                logger.error(f"Create/Replace rule request for rule with id {rule_id} failed", response)
                return {"message" : json.dumps(response.json()), "successfully_created": success_list}, status_code

            create_or_replace_rule_file(RULES_FOLDER, rule_id, rule)
            if rule_id not in rule_ids:
                rule_ids.append(rule_id)
            else:
                logger.warning(f"Rule already existed with rule id {rule_id}, it will be replaced")
            success_list.append(rule_id)

        logger.info(f"Post rules request successful for rules : {success_list}")
        return jsonify({"message": "Post rules request completed", "successfully_created": success_list}), 201
    except Exception as e:
        logger.error(f"Error occurred while creating rules: {str(e)}")
        return {"message" : "An error occurred while creating rules", "successfully_created": success_list}, 500


@rules_bp.route('/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """
    Delete a specific rule
    ---
    tags:
      - Rules
    operationId: deleteRule
    parameters:
      - name: rule_id
        in: path
        description: The ID of the rule to delete
        required: true
        schema:
          type: string
    responses:
      200:
        description: Successfully deleted the rule
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Rule not found
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """

    logger.debug(f"DELETE request received for rule with id {rule_id}")
    if rule_id not in rule_ids:
        return {"message":f"Rule with id {rule_id} not found"}, 404

    try:
        response = alertmanager.delete_rule(rule_id, ALERTMANAGER_URL) 
        status_code = response.status_code
        if status_code not in [200, 202, 204]:
            logger.error(f"Delete Rule request for rule with id {rule_id} failed: {response}")
            return response.json(), status_code

        rule_ids.remove(rule_id)
        delete_rule_file(RULES_FOLDER, rule_id)
        
        logger.info(f"DELETE request successful for rule with id {rule_id}")
        return jsonify({"message": f"Rule with id {rule_id} deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error occurred while deleting rule: {str(e)}")
        return {"message" : "An error occurred while deleting the rule"}, 500


@rules_bp.route('/rules', methods=['DELETE'])
def delete_all_rules():
    """
    Delete all rules
    ---
    tags:
      - Rules
    operationId: deleteAllRules
    responses:
      200:
        description: Successfully deleted all rules
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                successfully_deleted:
                  type: array
                  items:
                    type: string
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                successfully_deleted:
                  type: array
                  items:
                    type: string
    """
    logger.debug("DELETE request received for all rules")
    success_list = []
    try:
        for rule_id in rule_ids:
            response = alertmanager.delete_rule(rule_id, ALERTMANAGER_URL)
            status_code = response.status_code
            if status_code in [200, 202, 204]:
                delete_rule_file(RULES_FOLDER, rule_id)
                success_list.append(rule_id)

        for i in success_list:
            rule_ids.remove(i) 

        logger.info(f"DELETE request successful for rules : {success_list}")
        return {"message": "Rules deleted successfully", "successfully_deleted" : success_list}, 200
    except Exception as e:
        logger.error(f"Error occurred while deleting rules: {str(e)}")
        return {"message":"An error occurred while deleting the rules", "successfully_deleted" : success_list}, 500


@rules_bp.route('/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    """
    Get a specific rule by its ID
    ---
    tags:
      - Rules
    operationId: getRule
    parameters:
      - name: rule_id
        in: path
        description: The ID of the rule to retrieve
        required: true
        schema:
          type: string
    responses:
      200:
        description: Successfully retrieved the rule
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Rule'
      404:
        description: Rule not found
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """
    logger.debug(f"GET request received for rule with id {rule_id}")
    if rule_id not in rule_ids:
        return {"message":f"Rule with id {rule_id} not found"}, 404

    try:
        rule_data = read_rule_file(RULES_FOLDER, rule_id)

        logger.info(f"GET request successful for rule with id {rule_id}")
        return jsonify(rule_data), 200

    except Exception as e:
        logger.error(f"Error occurred while processing get request: {str(e)}")
        return {"message": "An error occurred while processing the request"}, 500


@rules_bp.route('/rules', methods=['GET'])
def get_all_rules():
    """
    Get all rules
    ---
    tags:
      - Rules
    operationId: getAllRules
    responses:
      200:
        description: Successfully retrieved all rules
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Rule'
      500:
        description: Internal server error
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
    """
    try:
        rules_list = []
        for rule_id in rule_ids:
            rule_data = read_rule_file(RULES_FOLDER, rule_id)
            rules_list.append(rule_data)
        logger.info("GET request complete for rules")
        return jsonify(rules_list), 200

    except Exception as e:
        logger.error(f"Error occurred while processing request: {str(e)}")
        return {"message" : "An error occurred while processing the request"}, 500
