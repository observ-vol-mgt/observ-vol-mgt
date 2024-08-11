# oTel-collector-proxy

The oTel collector proxy component is the Edge proxy allowing OVM Manager to control oTel collectors
and allow dynamic configuration of oTel processors as part of the collectors configuration.

The oTel collector proxy is deployed on each Edge location. The following functionalities are supported
by the proxy:

1. Communicates with OVM Manager over the control place - This communication is for configuration to be 
applied by the proxy to the oTel collector. The configuraiton is applied as a configuraiton file that is 
shared with the relavant oTel controller.

2. Configuration transformation - The OVM Manager confiration semantics is translated into oTel processor
configuration and saved into the configuration file

3. oTel collector update - As part of the oTel configuration update, the proxy performs a restart to the
collector to enforce the configuration changes (a limitation of the oTel collector) 

## Usage 

The oTel collector is configured using command line argument:

```bash
python rest_server.py --help
usage: rest_server.py [-h] --save-update-path SAVE_UPDATE_PATH --processor-file-to-update PROCESSOR_FILE_TO_UPDATE
                      --docker-container-reset-on-update DOCKER_CONTAINER_RESET_ON_UPDATE

Flask JSON Upload Server

options:
  -h, --help            show this help message and exit
  --save-update-path SAVE_UPDATE_PATH
                        Path where the updated YAML file will be saved
  --processor-file-to-update PROCESSOR_FILE_TO_UPDATE
                        oTel collector YAML file path - to be updated
  --docker-container-reset-on-update DOCKER_CONTAINER_RESET_ON_UPDATE
                        The name of the Docker container to reset on update
```

## Development

A Makefile is provided for basic operations:

```bash
$ make

Usage:
  make <target>
  help                  Display this help.

Docker
  docker_build          build to container
  docker_push           push to docker registry

Development
  run                   Execute the code
  tests                 Execute tests

CI
  ci_push               Executed upon ci push (merge) event
```

