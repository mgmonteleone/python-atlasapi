# Copyright (c) 2020 Matthew G. Monteleone
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

from datetime import datetime
from typing import Tuple, NewType, List, Optional

from dateutil.parser import parse
from enum import Enum
from pprint import pprint
from atlasapi.lib import logger
from atlasapi.whitelist import WhitelistEntry
import ipaddress
import requests
from awspublicranges.ranges import AwsIpRanges, AwsPrefix


class Roles(Enum):
    """Enum of the roles which can be assigned to a Atlas Public API Key

    """
    ORG_OWNER = 'ORG_OWNER'.replace('_', ' ').capitalize()
    ORG_MEMBER = 'ORG_OWNER'.replace('_', ' ').capitalize()
    ORG_GROUP_CREATOR = 'ORG_GROUP_CREATOR'.replace('_', ' ').capitalize()
    ORG_BILLING_ADMIN = 'ORG_BILLING_ADMIN'.replace('_', ' ').capitalize()
    ORG_READ_ONLY = 'ORG_READ_ONLY'.replace('_', ' ').capitalize()

    GROUP_CHARTS_ADMIN = 'GROUP_CHARTS_ADMIN'.replace('_', ' ').capitalize()
    GROUP_CLUSTER_MANAGER = 'GROUP_CLUSTER_MANAGER'.replace('_', ' ').capitalize()
    GROUP_DATA_ACCESS_ADMIN = 'GROUP_DATA_ACCESS_ADMIN'.replace('_', ' ').capitalize()
    GROUP_DATA_ACCESS_READ_ONLY = 'GROUP_DATA_ACCESS_READ_ONLY'.replace('_', ' ').capitalize()
    GROUP_DATA_ACCESS_READ_WRITE = 'GROUP_DATA_ACCESS_READ_WRITE'.replace('_', ' ').capitalize()
    GROUP_OWNER = 'GROUP_OWNER'.replace('_', ' ').capitalize()
    GROUP_READ_ONLY = 'GROUP_OWNER'.replace('_', ' ').capitalize()


class ApiKeyRoles(object):
    def __init__(self, group_id: str, org_id: str, role_name: Roles):
        """API roles assigned to an API key.

        Args:
            group_id:
            org_id:
            role_name: The role name itself.
        """
        self.role_name: Roles = role_name
        self.org_id: str = org_id
        self.group_id: str = group_id

    @classmethod
    def fill_from_dict(cls, data_dict: dict):
        """
        Fills the object from an Atlas Dict

        :param data_dict: A dict as returned from Atlas
        :return:
        """
        group_id = data_dict.get('groupId', None)
        org_id = data_dict.get('orgId', None)
        role_name: Roles = data_dict.get('roleName', None)

        return cls(group_id, org_id, role_name)


class ApiKey(object):
    def __init__(self, desc: str = None, id: str = None, private_key: str = None, public_key: str = None,
                 roles: List[ApiKeyRoles] = None):
        """An Atlas Pubic API access key

        Includes the roles assigned to each key.

        Args:
            desc:
            id:
            private_key:
            public_key:
            roles:
        """
        self.roles = roles
        self.public_key = public_key
        self.private_key = private_key
        self.id = id
        self.desc = desc

    @classmethod
    def fill_from_dict(cls, data_dict: dict):
        """
        Fills the object from an Atlas Dict

        :param data_dict: A dict as returned from Atlas
        :return:
        """
        desc = data_dict.get('desc', None)
        public_key = data_dict.get('publicKey', None)
        private_key = data_dict.get('privateKey', None)
        id = data_dict.get('id', None)
        roles_raw: List[dict] = data_dict.get('roles', None)
        roles: Optional[List[ApiKeyRoles]] = []
        for each_role in roles_raw:
            roles.append(ApiKeyRoles.fill_from_dict(data_dict=each_role))

        return cls(desc, id, private_key, public_key, roles)
