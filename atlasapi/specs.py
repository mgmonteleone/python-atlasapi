"""
Copyright (c) 2017 Yellow Pages Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from .settings import Settings

class RoleSpecs:
    """Roles supported by Atlas"""
    dbAdmin = "dbAdmin"
    readWrite = "readWrite"
    read = "read"

class DatabaseUsersPermissionsSpecs:
    """Permissions spec for Database User"""
    
    def __init__(self, username, password, databaseName=Settings.databaseName):
        """Constructor
        
        Args:
            username (str): Username of the DB
            password (str): Password for the username
            
        Kwargs:
            databaseName (str): Auth Database Name
        """
        self.username = username
        self.password = password
        self.databaseName = databaseName
        self.roles=[]
    
    def getSpecs(self):
        """Get specs
        
        Returns:
            dict. Representation of the object
        """
        content = {
            "databaseName" : self.databaseName,
            "roles" : self.roles,
            "username" : self.username,
            "password" : self.password
        }
        
        return content
    
    def add_roles(self, databaseName, roleNames):
        """Add multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
        """
        for roleName in roleNames:
            self.add_role(databaseName, roleName)
    
    def add_role(self, databaseName, roleName):
        """Add one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
        """
        role = {"databaseName" : databaseName,
                "roleName" : roleName}
        
        if role not in self.roles:
            self.roles.append(role)

    def remove_roles(self, databaseName, roleNames):
        """Remove multiple roles
        
        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles
        """
        for roleName in roleNames:
            self.remove_role(databaseName, roleName)
            
    def remove_role(self, databaseName, roleName):
        """Remove one role
        
        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role
        """
        role = {"databaseName" : databaseName,
                  "roleName" : roleName}
        
        if role in self.roles:
            self.roles.remove(role)
        
    def clear_roles(self):
        self.roles.clear()
        
class DatabaseUsersUpdatePermissionsSpecs(DatabaseUsersPermissionsSpecs):
    def __init__(self, password=None):
        """Constructor"""
        super().__init__(None, password)
    
    def getSpecs(self):
        """Get specs
        
        Returns:
            dict. Representation of the object
        """
        
        content = {}
        
        if len(self.roles) != 0:
            content["roles"] = self.roles
        
        if self.password:
            content["password"] = self.password
        
        return content
