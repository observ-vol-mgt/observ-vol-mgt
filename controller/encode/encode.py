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

import common.configuration_api as api

logger = logging.getLogger(__name__)


def encode(subtype, config, data):
    # switch based on the configuration ingest type
    # verify config parameters conform to structure
    if subtype == api.EncodeSubType.PIPELINE_ENCODE_SERIALIZED.value:
        # verify config parameters conform to structure
        typed_config = api.EncodeSerialized(**config)
        from encode.pickle_encode import encode
        encode(typed_config, data[0])
    else:
        raise "unsupported encode configuration"
    return data
