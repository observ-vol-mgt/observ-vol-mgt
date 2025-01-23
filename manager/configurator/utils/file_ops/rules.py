import os
import logging
import yaml

logger = logging.getLogger(__name__)

def load_rules(rules_folder):
    rule_ids = []
    for file in os.listdir(rules_folder):
        if file.endswith('.yaml'):
            rule_ids.append(os.path.basename(file).split('.yaml')[0])
    return rule_ids


def create_or_replace_rule_file(rules_folder, rule_id, rule_json):
    rule_yaml = yaml.dump(rule_json)
    with open(f"{rules_folder}/{rule_id}.yaml", 'w') as file:
        file.write(rule_yaml)

def delete_rule_file(rules_folder, rule_id):
    rule_file = f"{rules_folder}/{rule_id}.yaml"
    if os.path.exists(rule_file):
        os.remove(rule_file)

def read_rule_file(rules_folder, rule_id):
    rule_file = f"{rules_folder}/{rule_id}.yaml"
    with open(rule_file, 'r') as file:
        return yaml.safe_load(file)
