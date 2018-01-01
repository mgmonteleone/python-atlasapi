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
from .errors import ErrPaginationException, ErrPaginationLimitsException

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

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
        self.Projects = Atlas._Projects(self)
        self.Alerts = Atlas._Alerts(self)
    
    def isSuccess(self, code):
        return (code == Settings.SUCCESS)
    
    def isCreated(self, code):
        return (code == Settings.CREATED)
    
    def isAccepted(self, code):
        return (code == Settings.ACCEPTED)
        
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
                
            Returns:
                bool. The cluster exist or not
            """
            
            code, content = self.get_a_single_cluster(cluster)
            return self.atlas.isSuccess(code)
        
        def get_all_clusters(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Clusters
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-all/
            
            Kwargs:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                if iterable:
                    AtlasPagination. Iterable object representing this function
                elif:
                    int, dict. HTTP Code, Response payload
                    
            Raises:
                ErrPaginationLimitsException. Out of limits
            """
            
            # Check limits and raise an Exception if needed
            ErrPaginationLimitsException.checkAndRaise(pageNum, itemsPerPage)
            
            if iterable:
                return ClustersGetAll(self.atlas, pageNum, itemsPerPage)
            
            uri = Settings.api_resources["Clusters"]["Get All Clusters"] % (self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def get_a_single_cluster(self, cluster):
            """Get a Single Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/
            
            Args:
                cluster (str): The cluster name
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (self.atlas.group, cluster)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def delete_a_cluster(self, cluster, areYouSure = False):
            """Delete a Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/
            
            Args:
                cluster (str): Cluster name
                
            Kwargs:
                areYouSure (bool): safe flag to don't delete a cluster by mistake
            """
            if areYouSure:
                uri = Settings.api_resources["Clusters"]["Delete a Cluster"] % (self.atlas.group, cluster)
                return self.atlas.network.delete(Settings.BASE_URL + uri)
            else:
                return 400, { "detail" : "Please set areYouSure=True on delete_a_cluster call if you really want to delete [%s]" % cluster,
                              "error" : 400}
            
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
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                if iterable:
                    AtlasPagination. Iterable object representing this function
                elif:
                    int, dict. HTTP Code, Response payload
                    
            Raises:
                ErrPaginationLimitsException. Out of limits
            """
            
            # Check limits and raise an Exception if needed
            ErrPaginationLimitsException.checkAndRaise(pageNum, itemsPerPage)
            
            if iterable:
                return DatabaseUsersGetAll(self.atlas, pageNum, itemsPerPage)
            
            uri = Settings.api_resources["Database Users"]["Get All Database Users"] % (self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def get_a_single_database_user(self, user):
            """Get a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-single-user/
            
            Args:
                user (str): User
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Database Users"]["Get a Single Database User"] % (self.atlas.group, user)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def create_a_database_user(self, permissions):
            """Create a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/
            
            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Database Users"]["Create a Database User"] % self.atlas.group
            return self.atlas.network.post(Settings.BASE_URL + uri, permissions.getSpecs())
        
        def update_a_database_user(self, user, permissions):
            """Update a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-update-a-user/
            
            Args:
                user (str): User
                permissions (DatabaseUsersUpdatePermissionsSpecs): Permissions to apply
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Database Users"]["Update a Database User"] % (self.atlas.group, user)
            return self.atlas.network.patch(Settings.BASE_URL + uri, permissions.getSpecs())
        
        def delete_a_database_user(self, user):
            """Delete a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/
            
            Args:
                user (str): User to delete
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)
    
    class _Projects:
        """Projects API
        
        see: https://docs.atlas.mongodb.com/reference/api/projects/
        """
        
        def __init__(self, atlas):
            """_Projects constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
            
        def get_all_projects(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Projects
            
            url: https://docs.atlas.mongodb.com/reference/api/project-get-all/
            
            Kwargs:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                if iterable:
                    AtlasPagination. Iterable object representing this function
                elif:
                    int, dict. HTTP Code, Response payload
                    
            Raises:
                ErrPaginationLimitsException. Out of limits
            """
            
            # Check limits and raise an Exception if needed
            ErrPaginationLimitsException.checkAndRaise(pageNum, itemsPerPage)
            
            if iterable:
                return ProjectsGetAll(self.atlas, pageNum, itemsPerPage)
            
            uri = Settings.api_resources["Projects"]["Get All Projects"] % (pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def get_one_project(self, groupid):
            """Get one Project
            
            url: https://docs.atlas.mongodb.com/reference/api/project-get-one/
            
            Args:
                groupid (str): Group Id
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Projects"]["Get One Project"] % (groupid)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def create_a_project(self, name, orgId=None):
            """Create a Project
            
            url: https://docs.atlas.mongodb.com/reference/api/project-create-one/
            
            Args:
                name (str): Project name
                
            Kwargs:
                orgId (ObjectId): The ID of the organization you want to create the project within.
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Projects"]["Create a Project"]
            
            project = { "name" : name }
            if orgId:
                project["orgId"] = orgId
            
            return self.atlas.network.post(Settings.BASE_URL + uri, project)
        
    class _Alerts:
        """Clusters API
        
        see: https://docs.atlas.mongodb.com/reference/api/alerts/
        """
        
        def __init__(self, atlas):
            """_Cluster constructor
            
            Args:
                atlas (Atlas): Atlas instance
            """
            self.atlas = atlas
        
        def get_all_alerts(self, status=None, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Alerts
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/
            
            Kwargs:
                status (AlertStatusSpec): filter on alerts status
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                if iterable:
                    AtlasPagination. Iterable object representing this function
                elif:
                    int, dict. HTTP Code, Response payload
                    
            Raises:
                ErrPaginationLimitsException. Out of limits
            """
            
            # Check limits and raise an Exception if needed
            ErrPaginationLimitsException.checkAndRaise(pageNum, itemsPerPage)
            
            if iterable:
                return AlertsGetAll(self.atlas, status, pageNum, itemsPerPage)
            
            if status:
                uri = Settings.api_resources["Alerts"]["Get All Alerts with status"] % (self.atlas.group, status, pageNum, itemsPerPage)
            else:
                uri = Settings.api_resources["Alerts"]["Get All Alerts"] % (self.atlas.group, pageNum, itemsPerPage)
            
            return self.atlas.network.get(Settings.BASE_URL + uri)
            
        
        def get_an_alert(self, alert):
            """Get an Alert 
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-alert/
            
            Args:
                alert (str): The alert id
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            uri = Settings.api_resources["Alerts"]["Get an Alert"] % (self.atlas.group, alert)
            return self.atlas.network.get(Settings.BASE_URL + uri)
        
        def acknowledge_an_alert(self, alert, until, comment=None):
            """Acknowledge an Alert
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/
            
            Args:
                alert (str): The alert id
                until (datetime): Acknowledge until
                
            Kwargs:
                comment (str): The acknowledge comment
            
            Returns:
                int, dict. HTTP Code, Response payload
            """
            
            data = { "acknowledgedUntil" : until.isoformat(timespec='seconds') }
            if comment:
                data["acknowledgementComment"] = comment
            
            uri = Settings.api_resources["Alerts"]["Acknowledge an Alert"] % (self.atlas.group, alert)
            return self.atlas.network.patch(Settings.BASE_URL + uri, data)
        
        def unacknowledge_an_alert(self, alert):
            """Acknowledge an Alert
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/
            
            Args:
                alert (str): The alert id
                
            Returns:
                int, dict. HTTP Code, Response payload
            """
            
            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To unacknowledge a previously acknowledged alert, set the field value to the past.
            now = datetime.now(timezone.utc)
            until = now - relativedelta(days=1)
            return self.acknowledge_an_alert(alert, until)
        
        def acknowledge_an_alert_forever(self, alert, comment=None):
            """Acknowledge an Alert forever
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/
            
            Args:
                alert (str): The alert id
                
            Kwargs:
                comment (str): The acknowledge comment
            
            Returns:
                int, dict. HTTP Code, Response payload
            """
            
            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To acknowledge an alert “forever”, set the field value to 100 years in the future.
            now = datetime.now(timezone.utc)
            until = now + relativedelta(years=100)
            return self.acknowledge_an_alert(alert, until, comment)

class AtlasPagination:
    """Atlas Pagination Generic Implementation"""
    
    def __init__(self, atlas, fetch, pageNum, itemsPerPage):
        """Constructor
        
        Args:
            atlas (Atlas): Atlas instance
            fetch (function): The function "get_all" to call
            pageNum (int): Page number
            itemsPerPage (int): Number of Users per Page
        """
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
            # fetch the API
            c, details = self.fetch(pageNum, self.itemsPerPage)
            
            # handle errors
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
    """Pagination for Database User / Get All"""
    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)
        
class ProjectsGetAll(AtlasPagination):
    """Pagination for Projects / Get All"""
    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Projects.get_all_projects, pageNum, itemsPerPage)
        
class ClustersGetAll(AtlasPagination):
    """Pagination for Clusters / Get All"""
    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Clusters.get_all_clusters, pageNum, itemsPerPage)
        
class AlertsGetAll(AtlasPagination):
    """Pagination for Alerts / Get All"""
    def __init__(self, atlas, status, pageNum, itemsPerPage):
        super().__init__(atlas, self.fetch, pageNum, itemsPerPage)
        self.get_all_alerts = atlas.Alerts.get_all_alerts
        self.status = status
        
    def fetch(self, pageNum, itemsPerPage):
        return self.get_all_alerts(self.status, pageNum, itemsPerPage)
