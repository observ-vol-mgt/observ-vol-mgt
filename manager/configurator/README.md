# Manager

Manager: is deployed at the central cloud location and is responsible for managing observability data transformations at the edge locations. It is a user-facing component with a REST interface to create/update/delete the rules that define the transformation DAGs to be enabled on a certain edge site(s) when some condition is met. The user can also specify default transformation DAGs for edge sites. The Manager coordinates with the processors to enforce transformation DAGs based on user-defined rules when conditions are satisfied.

## Testing Locally

1. Specify the config file. A sample config YAML is present in [config/config.yaml](config/config.yaml). You need to specify the path to it using an environment variable. For example:
   ```bash
   export CONFIG_FILE=/path/to/your/config/config.yaml
   ```

2. Install all dependencies using [requirements.txt](requirement.txt):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python3 main.py
   ```


Once the application is running, it is accessible at `http://localhost:5010`.


### Processor Configuration APIs

All processor configuration APIs are available at `http://localhost:5010/api/v1/processor_config`.


### Rules APIs

All rules APIs are available at `http://localhost:5010/api/v1/rules`.

### Swagger UI

The Swagger UI is accessible at `http://localhost::5010/apidocs/`.
   
