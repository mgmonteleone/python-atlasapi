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

class RoleSpecs:
    """Roles supported by Atlas"""
    atlasAdmin = "atlasAdmin"
    readWriteAnyDatabase = "readWriteAnyDatabase"
    readAnyDatabase = "readAnyDatabase"
    backup = "backup"
    clusterMonitor = "clusterMonitor"
    dbAdmin = "dbAdmin"
    dbAdminAnyDatabase = "dbAdminAnyDatabase"
    enableSharding = "enableSharding"
    read = "read"
    readWrite = "readWrite"


class DatabaseUsersPermissionsSpecs:
    """Permissions spec for Database User
    
    Constructor
    
    Args:
        username (str): Username of the DB
        password (str): Password for the username
        
    Keyword Args:
        databaseName (str): Auth Database Name
    """

    def __init__(self, username, password, databaseName=Settings.databaseName):
        self.username = username
        self.password = password
        self.databaseName = databaseName
        self.roles = []

    def getSpecs(self):
        """Get specs
        
        Returns:
            dict: Representation of the object
        """
        content = {
            "databaseName": self.databaseName,
            "roles": self.roles,
            "username": self.username,
            "password": self.password
        }

        return content

    def add_roles(self, databaseName, roleNames, collectionName=None):
        """Add multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
            
        Keyword Args:
            collectionName (str): Collection
        
        Raises:
            ErrRoleException: role not compatible with the databaseName and/or collectionName
        """
        for roleName in roleNames:
            self.add_role(databaseName, roleName, collectionName)

    def add_role(self, databaseName, roleName, collectionName=None):
        """Add one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
            
        Keyword Args:
            collectionName (str): Collection
            
        Raises:
            ErrRole: role not compatible with the databaseName and/or collectionName
            :type databaseName: str
            :param databaseName:
            :type roleName: str
            :param collectionName:
        """
        role = {"databaseName": databaseName,
                "roleName": roleName}

        if collectionName:
            role["collectionName"] = collectionName

        # Check atlas constraints
        if collectionName and roleName not in [RoleSpecs.read, RoleSpecs.readWrite]:
            raise ErrRole("Permissions [%s] not available for a collection" % roleName)
        elif not collectionName and roleName not in [RoleSpecs.read, RoleSpecs.readWrite,
                                                     RoleSpecs.dbAdmin] and databaseName != "admin":
            raise ErrRole("Permissions [%s] is only available for admin database" % roleName)

        if role not in self.roles:
            self.roles.append(role)

    def remove_roles(self, databaseName, roleNames, collectionName=None):
        """Remove multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
            
        Keyword Args:
            collectionName (str): Collection
        """
        for roleName in roleNames:
            self.remove_role(databaseName, roleName, collectionName)

    def remove_role(self, databaseName, roleName, collectionName=None):
        """Remove one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
            
        Keyword Args:
            collectionName (str): Collection
        """
        role = {"databaseName": databaseName,
                "roleName": roleName}

        if collectionName:
            role["collectionName"] = collectionName

        if role in self.roles:
            self.roles.remove(role)

    def clear_roles(self):
        self.roles.clear()


class DatabaseUsersUpdatePermissionsSpecs(DatabaseUsersPermissionsSpecs):
    """Update Permissions spec for Database User
    
    Constructor
    
    Keyword Args:
        password (str): Password for the username
    """

    def __init__(self, password=None):
        super().__init__(None, password)

    def getSpecs(self):
        """Get specs
        
        Returns:
            dict: Representation of the object
        """

        content = {}

        if len(self.roles) != 0:
            content["roles"] = self.roles

        if self.password:
            content["password"] = self.password

        return content


class AlertStatusSpec:
    """Alert Status"""
    TRACKING = "TRACKING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


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
