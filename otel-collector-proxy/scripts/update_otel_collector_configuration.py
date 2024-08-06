import yaml
import logging

logger = logging.getLogger(__name__)


def update_processors(main_config_path, update_config_path, output_path):
    try:
        logging.info(f'Reading main configuration from {main_config_path}')
        with open(main_config_path, 'r') as main_file:
            main_config = yaml.safe_load(main_file)

        logging.info(f'Reading update configuration from {update_config_path}')
        with open(update_config_path, 'r') as update_file:
            update_config = yaml.safe_load(update_file)

        # Replace the processors section
        logging.info('Updating processors section in the main configuration')
        main_config['processors'] = update_config['processors']

        # Update the processors pipline section
        logging.info('Updating pipline')
        main_config['service']['pipelines']['metrics/1']['processors'] = list(main_config['processors'].keys())

        logging.info(f'Writing updated configuration to {output_path}')
        with open(output_path, 'w') as output_file:
            yaml.safe_dump(main_config, output_file)

        logging.info('Configuration update completed successfully')

    except Exception as e:
        logging.error(f'An error occurred: {e}')
        raise
