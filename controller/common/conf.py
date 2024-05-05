import configargparse

configuration = None


def get_configuration():
    return configuration


def parse_configuration():
    p = configargparse.ArgParser(
        default_config_files=['~/controller.config.yaml', 'config.yaml'])
    p.add('-c', '--config-file', required=False,
          is_config_file=True, help='config file path')
    p.add('-v', '--loglevel', help='logging level',
          default='info', env_var='LOGLEVEL')
    p.add('--ingest_type', help='ingest type (dummy, file or promql)',
          default='dummy', env_var='INGEST_TYPE')
    p.add('--ingest_file', help='ingest file ( for file type )',
          env_var='INGEST_FILE')
    p.add('--ingest_url', help='ingest url ( for promql type )',
          env_var='INGEST_URL')
    p.add('--ingest_window', help='ingest window ( for promql type )',
          env_var='INGEST_WINDOW')
    p.add('--feature_extraction_type', help='feature_extraction type (tsfel or tsfresh)',
          env_var='FEATURE_EXTRACTION_TYPE')
    p.add('--config_generator_type', help='configuration generation type (none, otel or processor)',
          default='none', env_var='CONFIG_GENERATOR_TYPE')
    p.add('--config_generator_directory', help='configuration generation output directory',
          env_var='CONFIG_GENERATOR_DIR')

    global configuration
    configuration = p.parse_args()
    print(configuration)
    print("----------")
    print(p.format_help())
    print("----------")
    print(p.format_values())
