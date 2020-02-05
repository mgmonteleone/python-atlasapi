# Copyright (c) 2019 Matthew G. Monteleone
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
# Modifications copyright (C) 2019 Matthew Monteleone

from enum import Enum
from typing import List, NewType, Optional, Union
from pprint import pprint
from datetime import datetime
import pytz
import uuid

FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class Alert(object):
    def __init__(self, data_dict: dict):
        self.alertConfigId: str = data_dict.get('alertConfigId', None)
        try:
            self.alertConfigId: Union[datetime, None] = datetime.strptime(data_dict.get("created", None),
                                                                          FORMAT).astimezone(tz=pytz.UTC)
        except ValueError:
            self.alertConfigId: Union[datetime, None] = None

        try:
            self.lastNotified: Union[datetime, None] = datetime.strptime(data_dict.get("lastNotified", None),
                                                                         FORMAT).astimezone(tz=pytz.UTC)
        except ValueError:
            self.lastNotified: Union[datetime, None] = None

        try:
            self.resolved: Union[datetime, None] = datetime.strptime(data_dict.get("resolved", None),
                                                                     FORMAT).astimezone(tz=pytz.UTC)
        except ValueError:
            self.resolved: Union[datetime, None] = None

        try:
            self.updated: Union[datetime, None] = datetime.strptime(data_dict.get("updated", None),
                                                                    FORMAT).astimezone(tz=pytz.UTC)
        except ValueError:
            self.updated: Union[datetime, None] = None

        self.currentValue: dict = data_dict.get('currentValue', None)
        self.eventTypeName: str = data_dict.get('eventTypeName', None)
        self.groupId: str = data_dict.get('groupId', None)
        self.hostnameAndPort: str = data_dict.get('hostnameAndPort', None)
        self.id: str = data_dict.get('id', None)
        self.links: list = data_dict.get('links', None)
        self.metricName: str = data_dict.get('metricName', None)
        self.replicaSetName: str = data_dict.get('replicaSetName', None)
        self.status: str = data_dict.get('status', None)
        self.typeName: str = data_dict.get('typeName', None)
