# Copyright (c) 2018 Yellow Pages Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Specs module

Provides some high level objects useful to use the Atlas API.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import open
from builtins import str


from .settings import Settings
from .errors import ErrRole
from datetime import datetime
from enum import Enum
from dateutil import parser
from .atlas_types import *
from typing import Optional, NewType, List, Any
from datetime import datetime
import isodate
from .lib import AtlasMeasurement

# etc., as needed

from future import standard_library
standard_library.install_aliases()


class ReplicaSetTypes(Enum):
    REPLICA_PRIMARY = 'ReplicaSet primary'
    REPLICA_SECONDARY = 'ReplicaSet secondary'
    RECOVERING = 'Recovering'
    SHARD_MONGOS = 'Mongos router'
    SHARD_CONFIG = 'Config server'
    SHARD_STANDALONE = 'Standalone'
    SHARD_PRIMARY = 'Shard primary'
    SHARD_SECONDARY = 'Shard secondary'
    NO_DATA = 'No data available'


class Host(object):
    """A Atlas host"""

    def __init__(self, data):
        """

        :type data: dict
        """
        if type(data) != dict:
            raise NotADirectoryError('The data parameter must be ann dict, you sent a {}'.format(type(data)))
        else:
            try:
                self.created = parser.parse(data.get("created", None))
            except (ValueError, OverflowError):
                self.create = data.get("created", None)
            self.group_id = data.get("group_id", None)
            self.hostname = data.get("hostname", None)
            self.id = data.get("id", None)

            try:
                self.last_ping = parser.parse(data.get("lastPing", None))
            except (ValueError, OverflowError):
                self.last_ping = data.get("lastPing", None)
            self.links = data.get("links", [])
            self.port = data.get("port", None)
            self.replica_set_name = data.get("replicaSetName", None)
            self.type = ReplicaSetTypes[data.get("typeName", "NO_DATA")]
            self.measurements = None


ListOfHosts = NewType('ListOfHosts', List[Optional[Host]])
