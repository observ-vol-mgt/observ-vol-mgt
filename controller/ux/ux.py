#   Copyright 2024 IBM, Inc.
#  #
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#  #
#       http://www.apache.org/licenses/LICENSE-2.0
#  #
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import os
from flask import Flask
from flasgger import Swagger

from ux.api import api
from ux.ui import ui
logger = logging.getLogger(__name__)

current_path = os.path.dirname(os.path.realpath(__file__))
flaskApp = Flask(__name__, template_folder=current_path,
                 static_folder=f"{current_path}/static")
flaskApp.register_blueprint(ui)
flaskApp.register_blueprint(api)
Swagger(flaskApp)


def start_ux():
    flaskApp.run(host="0.0.0.0", debug=False)
