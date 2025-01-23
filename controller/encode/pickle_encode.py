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

import logging
import pickle

logger = logging.getLogger(__name__)


def encode(encode_config, data):
    encode_file = encode_config.file_name

    logger.info(f"writing pickle format to {encode_file}")
    try:
        with open(encode_file, 'wb') as file:
            pickle.dump(data, file)
    except Exception as e:
        err = f"Error on file {encode_file}: {e}"
        raise RuntimeError(err) from e
    return data
