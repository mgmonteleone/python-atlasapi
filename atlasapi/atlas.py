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
Atlas module

Core module which provides access to MongoDB Atlas Cloud Provider APIs
"""

from .settings import Settings
from .network import Network
from .errors import *

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from .specs import Host, ListOfHosts
from typing import Union, Iterator
from .atlas_types import OptionalInt, OptionalBool, ListofDict
from .lib import AtlasPeriods, AtlasGranularities, AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement, \
    AtlasUnits, OptionalAtlasMeasurement
import logging
from pprint import pprint


# noinspection PyProtectedMember
class Atlas:
    """Atlas constructor
    
    Args:
        user (str): Atlas user
        password (str): Atlas password
        group (str): Atlas group
    """

    def __init__(self, user, password, group):
        self.group = group

        # Network calls which will handled user/password for auth
        self.network = Network(user, password)

        # APIs
        self.Clusters = Atlas._Clusters(self)
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
        self.Projects = Atlas._Projects(self)
        self.Alerts = Atlas._Alerts(self)
        self.Hosts = Atlas._Hosts(self)
        self.logger = logging.getLogger(name='Atlas')

    class _Clusters:
        """Clusters API
        
        see: https://docs.atlas.mongodb.com/reference/api/clusters/
        
        Constructor
        
        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def is_existing_cluster(self, cluster):
            """Check if the cluster exists
            
            Not part of Atlas api but provided to simplify some code
            
            Args:
                cluster (str): The cluster name
                
            Returns:
                bool: The cluster exists or not
            """

            try:
                self.get_a_single_cluster(cluster)
                return True
            except ErrAtlasNotFound:
                return False

        def get_all_clusters(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Clusters
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-all/
            
            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload
            
            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return ClustersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Clusters"]["Get All Clusters"] % (self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_a_single_cluster(self, cluster):
            """Get a Single Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/
            
            Args:
                cluster (str): The cluster name
            
            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (self.atlas.group, cluster)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def delete_a_cluster(self, cluster, areYouSure=False):
            """Delete a Cluster
            
            url: https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/
            
            Args:
                cluster (str): Cluster name
                
            Keyword Args:
                areYouSure (bool): safe flag to don't delete a cluster by mistake
                
            Returns:
                dict: Response payload
                
            Raises:
                ErrConfirmationRequested: Need a confirmation to delete the cluster


                :param cluster:  Cluster name
                :param areYouSure: safe flag to don't delete a cluster by mistake

            """
            if areYouSure:
                uri = Settings.api_resources["Clusters"]["Delete a Cluster"] % (self.atlas.group, cluster)
                return self.atlas.network.delete(Settings.BASE_URL + uri)
            else:
                raise ErrConfirmationRequested(
                    "Please set areYouSure=True on delete_a_cluster call if you really want to delete [%s]" % cluster)

    class _DatabaseUsers:
        """Database Users API
        
        see: https://docs.atlas.mongodb.com/reference/api/database-users/
        
        Constructor
        
        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_database_users(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Database Users
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-all-users/
            
            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload
                    
            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return DatabaseUsersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Database Users"]["Get All Database Users"] % (
                self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_a_single_database_user(self, user):
            """Get a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-single-user/
            
            Args:
                user (str): User
                
            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Get a Single Database User"] % (self.atlas.group, user)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_a_database_user(self, permissions):
            """Create a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/
            
            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply
                
            Returns:
                dict: Response payload
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
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Update a Database User"] % (self.atlas.group, user)
            return self.atlas.network.patch(Settings.BASE_URL + uri, permissions.getSpecs())

        def delete_a_database_user(self, user):
            """Delete a Database User
            
            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/
            
            Args:
                user (str): User to delete
                
            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

    class _Projects:
        """Projects API
        
        see: https://docs.atlas.mongodb.com/reference/api/projects/
        
        Constructor
        
        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_projects(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Projects
            
            url: https://docs.atlas.mongodb.com/reference/api/project-get-all/
            
            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload
                    
            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

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
                dict: Response payload
            """
            uri = Settings.api_resources["Projects"]["Get One Project"] % groupid
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_a_project(self, name, orgId=None):
            """Create a Project
            
            url: https://docs.atlas.mongodb.com/reference/api/project-create-one/
            
            Args:
                name (str): Project name
                
            Keyword Args:
                orgId (ObjectId): The ID of the organization you want to create the project within.
                
            Returns:
                dict: Response payload
                :param name:
                :param orgId:
            """
            uri = Settings.api_resources["Projects"]["Create a Project"]

            project = {"name": name}
            if orgId:
                project["orgId"] = orgId

            return self.atlas.network.post(Settings.BASE_URL + uri, project)

    class _Alerts:
        """Alerts API
        
        see: https://docs.atlas.mongodb.com/reference/api/alerts/
        
        Constructor
        
        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_alerts(self, status=None, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage,
                           iterable=False):
            """Get All Alerts
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/
            
            Keyword Args:
                status (AlertStatusSpec): filter on alerts status
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response
                
            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload
                    
            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return AlertsGetAll(self.atlas, status, pageNum, itemsPerPage)

            if status:
                uri = Settings.api_resources["Alerts"]["Get All Alerts with status"] % (
                    self.atlas.group, status, pageNum, itemsPerPage)
            else:
                uri = Settings.api_resources["Alerts"]["Get All Alerts"] % (self.atlas.group, pageNum, itemsPerPage)

            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_an_alert(self, alert):
            """Get an Alert 
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-alert/
            
            Args:
                alert (str): The alert id
                
            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Alerts"]["Get an Alert"] % (self.atlas.group, alert)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def acknowledge_an_alert(self, alert, until, comment=None):
            """Acknowledge an Alert
            
            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/
            
            Args:
                alert (str): The alert id
                until (datetime): Acknowledge until
                
            Keyword Args:
                comment (str): The acknowledge comment
            
            Returns:
                dict: Response payload
                :param until:
                :param alert:
                :param comment:
            """

            data = {"acknowledgedUntil": until.isoformat(timespec='seconds')}
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
                dict: Response payload
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
                
            Keyword Args:
                comment (str): The acknowledge comment
            
            Returns:
                dict: Response payload
                :param alert:
                :param comment:
            """

            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To acknowledge an alert “forever”, set the field value to 100 years in the future.
            now = datetime.now(timezone.utc)
            until = now + relativedelta(years=100)
            return self.acknowledge_an_alert(alert, until, comment)

    class _Hosts:
        """Hosts API

        see: https://docs.atlas.mongodb.com/reference/api/monitoring-and-logs/#monitoring-and-logs

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas
            self.logger = logging.getLogger('Atlas.Hosts')

        def _get_all_hosts(self, pageNum=Settings.pageNum,
                           itemsPerPage=Settings.itemsPerPage,
                           iterable=False):
            """Get All Hosts (actually processes)

            Internal use only, actual data retrieval comes from properties host_list and host_names
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                ListOfHosts or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
                :rtype: Union[ListOfHosts, dict]
                :type iterable: OptionalBool
                :type itemsPerPage: OptionalInt
                :type pageNum: OptionalInt

            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                item_list = list(HostsGetAll(self.atlas, pageNum, itemsPerPage))
                obj_list = list()
                for item in item_list:
                    obj_list.append(Host(item))
                return_val = obj_list
            else:
                uri = Settings.api_resources["Monitoring and Logs"]["Get all processes for group"].format(
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage)

                return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            return return_val

        @property
        def host_list(self):
            """Returns a list of Host Objects
            :rtype: ListOfHosts
            """

            return self._get_all_hosts(iterable=True)

        @property
        def host_names(self):
            """Returns a simple list of host names without port
            :rtype: Iterator[str]
            """

            for host in self.host_list:
                yield host.hostname

        def _get_measurement_for_host(self, host_obj, granularity=AtlasGranularities.HOUR, period=AtlasPeriods.WEEKS_1,
                                      measurement=AtlasMeasurementTypes.Cache.dirty, pageNum=Settings.pageNum,
                                      itemsPerPage=Settings.itemsPerPage, iterable=False) -> OptionalAtlasMeasurement:
            """Get  measurement(s_ for a host

            Internal use only, actual data retrieval comes from properties host_list and host_names
            url: https://docs.atlas.mongodb.com/reference/api/process-measurements/

            Accepts either a single measurement, but will retrieve more than one measurement
            if the measurement (using the AtlasMeasurementTypes class)



            /api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/measurements

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                ListOfHosts or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits

                :type iterable: OptionalBool
                :type itemsPerPage: OptionalInt
                :type pageNum: OptionalInt
                :type period: AtlasPeriods
                :type granularity: AtlasGranularities
                :type host_obj: Host
                :type measurement: AtlasMeasurementTypes

            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            # Check to see if we received a leaf or branch of the measurements
            try:
                parent = super(measurement)
                self.logger.warning('We received a branch.')
                leaves = measurement.get_all()
                measurement_list = list(leaves)
                measurement = '&m='.join(measurement_list)
                got_leaf = False
            except TypeError as e:
                got_leaf = True
                self.logger.warning('We received a leaf')


            # Build the URL
            uri = Settings.api_resources["Monitoring and Logs"]["Get measurement for host"].format(
                group_id=self.atlas.group,
                host=host_obj.hostname,
                port=host_obj.port,
                granularity=granularity,
                period=period,
                measurement=measurement

                # page_num=pageNum,
                # items_per_page=itemsPerPage
            )
            # Build the request
            return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            if iterable:
                measurements = return_val.get('measurements')
                measurements_count = len(measurements)
                self.logger.warning('There are {} measurements.'.format(measurements_count))
                measurement_obj = None
                if measurements_count == 1:
                    measurement_obj = AtlasMeasurement(name=measurement
                                                       , period=period
                                                       , granularity=granularity)
                    for each in measurements[0].get('dataPoints'):
                        measurement_obj.measurements = AtlasMeasurementValue(each)
                    return measurement_obj

                else:
                    self.logger.warning('Yipeee, we got {} measurements,'
                                        ' now we gotta process them'.format(measurements_count))
                    measurements_list = list()
                    for each in measurements:
                        measurement_obj = AtlasMeasurement(name=each.get('name')
                                                       , period=period
                                                       , granularity=granularity)
                        for each_and_every in each.get('dataPoints'):
                            measurement_obj.measurements = AtlasMeasurementValue(each_and_every)
                        measurements_list.append(measurement_obj)
                return measurements_list

            else:
                return return_val


class AtlasPagination:
    """Atlas Pagination Generic Implementation
    
    Constructor
        
    Args:
        atlas (Atlas): Atlas instance
        fetch (function): The function "get_all" to call
        pageNum (int): Page number
        itemsPerPage (int): Number of Users per Page
    """

    def __init__(self, atlas, fetch, pageNum, itemsPerPage):
        self.atlas = atlas
        self.fetch = fetch
        self.pageNum = pageNum
        self.itemsPerPage = itemsPerPage

    def __iter__(self):
        """Iterable
        
        Yields:
            str: One result
        """

        # pageNum is set with the value requested (so not necessary 1)
        pageNum = self.pageNum
        # total: This is a fake value to enter into the while. It will be updated with a real value later
        total = pageNum * self.itemsPerPage

        while pageNum * self.itemsPerPage - total < self.itemsPerPage:
            # fetch the API
            try:
                details = self.fetch(pageNum, self.itemsPerPage)
            except Exception:
                raise ErrPagination()

            # set the real total
            total = details["totalCount"]

            # while into the page results
            results = details["results"]
            results_count = len(results)
            index = 0
            while index < results_count:
                result = results[index]
                index += 1
                yield result

            # next page
            pageNum += 1


class DatabaseUsersGetAll(AtlasPagination):
    """Pagination for Database User : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)


class ProjectsGetAll(AtlasPagination):
    """Pagination for Projects : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Projects.get_all_projects, pageNum, itemsPerPage)


class ClustersGetAll(AtlasPagination):
    """Pagination for Clusters : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Clusters.get_all_clusters, pageNum, itemsPerPage)


class AlertsGetAll(AtlasPagination):
    """Pagination for Alerts : Get All"""

    def __init__(self, atlas, status, pageNum, itemsPerPage):
        super().__init__(atlas, self.fetch, pageNum, itemsPerPage)
        self.get_all_alerts = atlas.Alerts.get_all_alerts
        self.status = status

    def fetch(self, pageNum, itemsPerPage):
        """Intermediate fetching
        
        Args:
            pageNum (int): Page number
            itemsPerPage (int): Number of Users per Page
            
        Returns:
            dict: Response payload
        """
        return self.get_all_alerts(self.status, pageNum, itemsPerPage)


# noinspection PyProtectedMember
class HostsGetAll(AtlasPagination):
    """Pagination for Processes : Get All"""

    def __init__(self, atlas: Atlas, pageNum: int, itemsPerPage: int):
        super().__init__(atlas, atlas.Hosts._get_all_hosts, pageNum, itemsPerPage)
