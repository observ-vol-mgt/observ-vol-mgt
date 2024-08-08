#  Copyright 2024 IBM, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import docker
import logging

logger = logging.getLogger(__name__)


def restart_docker_container(container_name):
    # Initialize the Docker client
    client = docker.from_env()

    try:
        # Get the container
        container = client.containers.get(container_name)

        # Restart the container
        container.restart()

        logger.info(f"Container '{container_name}' restarted successfully.")
    except docker.errors.NotFound:
        logger.error(f"Container '{container_name}' not found.")
    except docker.errors.APIError as e:
        logger.error(f"Failed to restart container '{container_name}': {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
