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

from .settings import Settings
from .errors import ErrRole

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
        self.roles=[]
    
    def getSpecs(self):
        """Get specs
        
        Returns:
            dict: Representation of the object
        """
        content = {
            "databaseName" : self.databaseName,
            "roles" : self.roles,
            "username" : self.username,
            "password" : self.password
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
        """
        role = {"databaseName" : databaseName,
                "roleName" : roleName}
        
        if collectionName:
            role["collectionName"] = collectionName
        
        # Check atlas constraints
        if collectionName and roleName not in [RoleSpecs.read, RoleSpecs.readWrite]:
            raise ErrRole("Permissions [%s] not available for a collection" % roleName)
        elif not collectionName and roleName not in [RoleSpecs.read, RoleSpecs.readWrite, RoleSpecs.dbAdmin] and databaseName != "admin":
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
        role = {"databaseName" : databaseName,
                "roleName" : roleName}
        
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
