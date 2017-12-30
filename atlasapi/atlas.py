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

import requests
from .settings import Settings
from .network import Network
from .errors import ErrPaginationException

class Atlas:
    def __init__(self, user, password, group):
        """Atlas constructor
        
        Args:
            user (str): Atlas user
            password (str): Atlas password
            group (str): Atlas group
        """
        
        self.group = group
        
        # Network calls which will handld user/passord for auth
        self.network = Network(user, password)
        
        # APIs
        self.Clusters = Atlas._Clusters(self)
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
    
    def isSuccess(self, code):
        return (code == Settings.SUCCESS)
    
    def isCreated(self, code):
        return (code == Settings.CREATED)
        
    class _Clusters:
        """Clusters API
        
        see: https://docs.atlas.mongodb.com/reference/api/clusters/
        """
        
        def __init__(self, atlas):
            """_Cluster constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
            
        def is_existing_cluster(self, cluster):
            """Check if the cluster exists
            
            Not part of Atlas api but provided to simplify some code
            
            Args:
                cluster (str): The cluster name
            """
            
            code, content = self.get_a_single_cluster(cluster)
            return self.atlas.isSuccess(code)
        
        def get_a_single_cluster(self, cluster):
            """Get a Single Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/
            
            Args:
                cluster (str): The cluster name
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (self.atlas.group, cluster)
            return self.atlas.network.get(Settings.BASE_URL + uri)
            
    class _DatabaseUsers:
        """Database Users API
        
        see: https://docs.atlas.mongodb.com/reference/api/database-users/
        """
        
        def __init__(self, atlas):
            """_DatabaseUsers constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
            
        def get_all_database_users(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Database Users
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-all-users/
            
            Kwargs:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
            """
            
            # Enforce Atlas limitation if needed
            if itemsPerPage > Settings.itemsPerPageMax:
                itemsPerPage = Settings.itemsPerPageMax
            
            uri = Settings.api_resources["Database Users"]["Get All Database Users"] % (self.atlas.group, pageNum, itemsPerPage)
            
            if iterable:
                return DatabaseUsersGetAll(self.atlas, pageNum, itemsPerPage)
            else:
                return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def get_a_single_database_user(self, user):
            """Get a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-single-user/
            
            Args:
                user (str): User
            """
            uri = Settings.api_resources["Database Users"]["Get a Single Database User"] % (self.atlas.group, user)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def create_a_database_user(self, permissions):
            """Create a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/
            
            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply
            """
            uri = Settings.api_resources["Database Users"]["Create a Database User"] % self.atlas.group
            return self.atlas.network.post(Settings.BASE_URL + uri, permissions.getSpecs())
        
        def update_a_database_user(self, user, permissions):
            """Update a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-update-a-user/
            
            Args:
                user (str): User
                permissions (DatabaseUsersUpdatePermissionsSpecs): Permissions to apply
            """
            uri = Settings.api_resources["Database Users"]["Update a Database User"] % (self.atlas.group, user)
            return self.atlas.network.patch(Settings.BASE_URL + uri, permissions.getSpecs())
        
        def delete_a_database_user(self, user):
            """Delete a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/
            
            Args:
                user (str): User to delete
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

class AtlasPagination:
    def __init__(self, atlas, fetch, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage):
        self.atlas = atlas
        self.fetch = fetch
        self.pageNum = pageNum
        self.itemsPerPage = itemsPerPage
    
    def __iter__(self):
        # pageNum is set with the value requested (so not necessary 1)
        pageNum = self.pageNum
        # total: This is a fake value to enter into the while. It will be updated with a real value later
        total = pageNum * self.itemsPerPage
        
        while (pageNum * self.itemsPerPage - total < self.itemsPerPage):
            c, details = self.fetch(pageNum, self.itemsPerPage)
            if not self.atlas.isSuccess(c):
                raise ErrPaginationException()
            
            # set the real total
            total = details["totalCount"]
            
            # while into the page results
            results = details["results"]
            results_count = len(results)
            index = 0
            while (index < results_count):
                user = results[index]
                index += 1
                yield user
            
            # next page
            pageNum += 1
            
class DatabaseUsersGetAll(AtlasPagination):
    def __init__(self, atlas, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage):
        super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)
