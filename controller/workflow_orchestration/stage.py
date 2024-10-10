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

from common.configuration_api import BaseStageParameters


class StageParameters:
    def __init__(self, stg):
        self.base_stage = BaseStageParameters(**stg)
        self.follows = []
        self.followers = []
        self.latest_output_data = None
        self.scheduled = False

    def set_follows(self, stage):
        self.follows.append(stage)

    def add_follower(self, stage):
        self.followers.append(stage)

    def set_latest_output_data(self, output_data):
        self.latest_output_data = output_data

    def set_scheduled(self):
        self.scheduled = True

    def clear_scheduled(self):
        self.scheduled = False
