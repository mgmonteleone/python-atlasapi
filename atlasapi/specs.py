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
from typing import Optional, NewType, List, Any, Union, Iterable, BinaryIO
from datetime import datetime
import isodate
from .measurements import AtlasMeasurement, AtlasMeasurementTypes
from .lib import AtlasGranularities, AtlasPeriods, AtlasLogNames
import logging
from future import standard_library

standard_library.install_aliases()
logger = logging.getLogger('Atlas.specs')


# etc., as needed

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
    SHARD_CONFIG_PRIMARY = 'Config server'
    SHARD_CONFIG_SECONDARY = 'Config server'


class HostLogFile(object):
    def __init__(self, log_name: AtlasLogNames = None, log_file_binary: BinaryIO = None ):
        """Container for Atlas log files for a host instance

        Args:
            log_name (AtlasLogName): They type of log file
            log_file_binary (BinaryIO): The binary of the gzipped log file
        """
        self.log_file_binary = log_file_binary
        self.log_name = log_name


class Host(object):
    """
        An Atlas Host

        Args:
            data (dict): An Atlas format host data dictionary.

        Attributes:
            created (datetime): The datetime the host was created.
            group_id (str): The Atlas group(project) id that this host belongs to
            hostname (str): The fqdn hostname
            id (str): The internal atlas id of the host.
            last_ping (Union[datetime,str]): The datetime of the last Automation Agent ping
            links (List[str]): A list of internal reference links for the host
            port (int): The TCP port the instance is running on.
            replica_set_name (str): The name of the replica set running on the instance
            type (ReplicaSetTypes): The type of replica set this intstance is a member of
            measurements (Optional[List[AtlasMeasurement]]: Holds list of host Measurements
            cluster_name (str): The cluster name (taken from the hostname)
            log_files (Optional[List[HostLogFile]]): Holds list of log files when requested.

    """
    def __init__(self, data):
        if type(data) != dict:
            raise NotADirectoryError('The data parameter must be ann dict, you sent a {}'.format(type(data)))
        else:
            try:
                self.created: datetime = parser.parse(data.get("created", None))
            except (ValueError, OverflowError):
                self.created = data.get("created", None)
            self.group_id: str = data.get("group_id", None)
            self.hostname: str = data.get("hostname", None)
            self.id: str = data.get("id", None)

            try:
                self.last_ping = parser.parse(data.get("lastPing", None))
            except (ValueError, OverflowError):
                self.last_ping = data.get("lastPing", None)
            self.links = data.get("links", [])
            self.port = data.get("port", None)
            self.replica_set_name = data.get("replicaSetName", None)
            self.type = ReplicaSetTypes[data.get("typeName", "NO_DATA")]
            self.measurements = []
            self.cluster_name = self.hostname.split('-')[0]
            self.log_files: Optional[List[HostLogFile]] = None

    def get_measurement_for_host(self, granularity: AtlasGranularities = AtlasGranularities.HOUR,
                                 period: AtlasPeriods = AtlasPeriods.WEEKS_1,
                                 measurement: AtlasMeasurementTypes = AtlasMeasurementTypes.Cache.dirty,
                                 pageNum: int = Settings.pageNum,
                                 itemsPerPage: int = Settings.itemsPerPage,
                                 iterable: bool = True) -> Union[dict, Iterable[AtlasMeasurement]]:
        """Get  measurement(s) for a host

        Returns measurements for the Host object.

        url: https://docs.atlas.mongodb.com/reference/api/process-measurements/


        Accepts either a single measurement, but will retrieve more than one measurement
        if the measurement (using the AtlasMeasurementTypes class)

        /api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/measurements

        Keyword Args:
            host_obj (Host): the host
            granularity (AtlasGranularities): the desired granularity
            period (AtlasPeriods): The desired period
            measurement (AtlasMeasurementTypes) : The desired measurement or Measurement class
            pageNum (int): Page number
            itemsPerPage (int): Number of Users per Page
            iterable (bool): To return an iterable high level object instead of a low level API response

        Returns:
             Iterable[AtlasMeasurement] or dict: Iterable object representing this function OR Response payload

        Raises:
            ErrPaginationLimits: Out of limits


        """

        # Check limits and raise an Exception if needed
        ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

        # Check to see if we received a leaf or branch of the measurements
        try:
            parent = super(measurement)
            self.logger.info('We received a branch, whos parent is {}'.format(parent.__str__()))
            leaves = measurement.get_all()
            measurement_list = list(leaves)
            measurement = '&m='.join(measurement_list)
        except TypeError:
            self.logger.info('We received a leaf')

        # Build the URL
        uri = Settings.api_resources["Monitoring and Logs"]["Get measurement for host"].format(
            group_id=self.atlas.group,
            host=host_obj.hostname,
            port=host_obj.port,
            granularity=granularity,
            period=period,
            measurement=measurement
        )
        # Build the request
        return_val = self.atlas.network.get(Settings.BASE_URL + uri)
        measurement_obj = None
        if iterable:
            measurements = return_val.get('measurements')
            measurements_count = len(measurements)
            self.logger.info('There are {} measurements.'.format(measurements_count))

            for each in measurements:
                measurement_obj = AtlasMeasurement(name=each.get('name'),
                                                   period=period,
                                                   granularity=granularity)
                for each_and_every in each.get('dataPoints'):
                    measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

            yield measurement_obj

        else:
            return return_val

    def add_measurements(self, measurement) -> None:
        # TODO: Make measurements unique, use a set instead, but then how do we concat 2?
        self.measurements = self.measurements + measurement

    def add_log_file(self, name: AtlasLogNames, file: BinaryIO) -> None:
        """
        Adds the passed log file to the hosts object

        Args:
            name (AtlasLogNames): The type of logfile to be appended.
            file (BinaryIO): The file to be appended
        """
        log_obj = HostLogFile(log_name=name, log_file_binary=file)
        if self.log_files is None:
            self.log_files = [log_obj]
        else:
            self.log_files.append(log_obj)

    def __hash__(self):
        return hash(self.hostname)

    def __eq__(self, other):
        if isinstance(other, Host):
            return self.hostname == other.hostname


ListOfHosts = NewType('ListOfHosts', List[Optional[Host]])


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

    def __init__(self, username: str, password: str, databaseName=Settings.databaseName) -> None:
        self.username = username
        self.password = password
        self.databaseName = databaseName
        self.roles = []

    def getSpecs(self) -> dict:
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

    def add_roles(self, databaseName: str, roleNames: List[RoleSpecs], collectionName: str = None):
        """Add multiple roles

        Args:
            databaseName (str): Database Name
            roleNames (list of RoleSpecs): roles

        Keyword Args:
            collectionName (str): Collection

        Raises:
            ErrRoleException: role not compatible with the databaseName and/or collectionName
            :param databaseName: Database Name
            :param roleNames: roles
            :param collectionName: Collection

        """
        for roleName in roleNames:
            self.add_role(databaseName, roleName, collectionName)

    def add_role(self, databaseName: str, roleName: str, collectionName: OptionalStr = None):
        """Add one role

        Args:
            databaseName (str): Database Name
            roleName (RoleSpecs): role

        Keyword Args:
            collectionName (str): Collection

        Raises:
            ErrRole: role not compatible with the databaseName and/or collectionName
            :param roleName:
            :param databaseName:
            :type collectionName: str
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
