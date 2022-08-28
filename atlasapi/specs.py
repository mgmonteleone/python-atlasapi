# Copyright (c) 2022 Matthew G. Monteleone
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

from builtins import str

from atlasapi.lib import logger

from atlasapi.settings import Settings
from atlasapi.errors import ErrRole

from enum import Enum
from dateutil import parser
from atlasapi.atlas_types import *
from typing import Optional, NewType, List, Union, Iterable, BinaryIO, Any
from datetime import datetime
from atlasapi.lib import AtlasGranularities, AtlasPeriods, AtlasLogNames
import logging
from future import standard_library
from logging import Logger
from pprint import pprint
from atlasapi.measurements import AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement
from requests.compat import urljoin
from urllib.parse import urlencode

standard_library.install_aliases()
logger: Logger = logging.getLogger('Atlas.specs')


# etc., as needed


class IAMType(Enum):
    NONE = 'None'  # The user does not use AWS IAM credentials.
    USER = 'USER'  # New database user has AWS IAM user credentials.
    ROLE = 'ROLE'  # New database user has credentials associated with an AWS IAM role.


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
    def __init__(self, log_name: AtlasLogNames = None, log_file_binary: BinaryIO = None):
        """Container for Atlas log files for a host instance

        Args:
            log_name (AtlasLogName): They type of log file
            log_file_binary (BinaryIO): The binary of the gzipped log file
        """
        self.log_file_binary = log_file_binary
        self.log_name = log_name


class Host(object):
    def __init__(self, data: dict) -> None:
        """An Atlas Host
            Contains all basic information for an Atlas host.
            Using various methods, enables the retrieval of more advanced data, such as measurements and log files.

        Args:
            data(dict): An Atlas format host data dictionary.

        Attributes:
            created (datetime): The datetime the host was created.
            group_id (str): The Atlas group(project) id that this host belongs to
            hostname (str): The fqdn hostname
            hostname_alias (str) : User-friendly hostname of the cluster node. The user-friendly hostname is typically
             the standard hostname for a cluster node and it appears in the connection string for a cluster instead of
             the value of the hostname field.
            id (str): The internal atlas id of the host.
            last_ping (Union[datetime,str]): The datetime of the last Automation Agent ping
            links (List[str]): A list of internal reference links for the host
            port (int): The TCP port the instance is running on.
            replica_set_name (str): The name of the replica set running on the instance
            type (ReplicaSetTypes): The type of replica set this intstance is a member of
            measurements (Optional[List[measurements.AtlasMeasurement]]: Holds list of host Measurements
            cluster_name (str): The cluster name (taken from the hostname)
            cluster_name_alias (str) : The cluster name user alias, taken from the hostname user friendly alias.
            log_files (Optional[List[HostLogFile]]): Holds list of log files when requested.
        """
        if type(data) != dict:
            raise NotADirectoryError('The data parameter must be ann dict, you sent a {}'.format(type(data)))
        else:
            try:
                self.created: datetime = parser.parse(data.get("created", None))
            except (ValueError, OverflowError):
                self.created = data.get("created", None)
            self.group_id: str = data.get("groupId", None)
            self.hostname: str = data.get("hostname", None)
            self.hostname_alias: str = data.get("userAlias", self.hostname)
            self.id: str = data.get("id", None)
            try:
                self.last_ping = parser.parse(data.get("lastPing", None))
            except (ValueError, OverflowError, TypeError):
                self.last_ping = data.get("lastPing", None)
            self.links: Optional[List[str]] = data.get("links", [])
            self.port: Optional[int] = data.get("port", None)
            self.replica_set_name: Optional[str] = data.get("replicaSetName", None)
            self.type: OptionalStr = ReplicaSetTypes[data.get("typeName", "NO_DATA")]
            self.measurements: Optional[List[AtlasMeasurement]] = []

            # NOTE: cluster_name_alias is NOT reliable since it relies on parsing the hostname_alias, which is
            # lowercased. If the clustername_alias uses any casing, this will not be usuable.

            if '-shard-' in self.hostname_alias:
                self.cluster_name_alias: str = self.hostname_alias.split('-shard-')[0]
            elif '-config-' in self.hostname_alias:
                self.cluster_name_alias: str = self.hostname_alias.split('-config-')[0]
            else:
                self.cluster_name_alias: str = self.hostname_alias.split('-')[0]

            if '-shard-' in self.hostname:
                self.cluster_name: str = self.hostname.split('-shard-')[0]
            elif '-config-' in self.hostname:
                self.cluster_name: str = self.hostname.split('-config-')[0]
            else:
                self.cluster_name: str = self.hostname.split('-')[0]

            self.log_files: Optional[List[HostLogFile]] = None

    def get_measurement_for_host(self, atlas_obj, granularity: Optional[AtlasGranularities] = None,
                                 period: Optional[AtlasPeriods] = None,
                                 measurement: Optional[AtlasMeasurementTypes] = None
                                 ) -> Union[dict, Iterable[AtlasMeasurement]]:
        """Get  measurement(s) for a host

        Returns measurements for the Host object.

        url: https://docs.atlas.mongodb.com/reference/api/process-measurements/


        Accepts either a single measurement, but will retrieve more than one measurement
        if the measurement (using the AtlasMeasurementTypes class)

        /api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/measurements

        Keyword Args:
            Atlas obj (Atlas): the host
            granularity (AtlasGranularities): the desired granularity
            period (AtlasPeriods): The desired period
            measurement (AtlasMeasurementTypes) : The desired measurement or Measurement class
            iterable (bool): To return an iterable high level object instead of a low level API response

        Returns:
             Iterable[AtlasMeasurement] or dict: Iterable object representing this function OR Response payload

        Raises:


        """

        # Set default
        if measurement is None:
            measurement = AtlasMeasurementTypes.Cache.dirty
            logger.info(f'The measurement is {measurement}')
        if period is None:
            period = AtlasPeriods.WEEKS_1
        logger.info(f'The granularity is {granularity}')

        if granularity is None:
            granularity = AtlasGranularities.HOUR
        logger.info(f'The granularity is {granularity}')

        # Check to see if we received a leaf or branch of the measurements
        try:
            parent = super(measurement)
            logger.info('We received a branch, whos parent is {}'.format(parent.__str__()))
            leaves = measurement.get_all()
            measurement_list = list(leaves)
            measurement = '&m='.join(measurement_list)
        except TypeError:
            logger.info('We received a leaf')

        # Build the URL
        uri = Settings.api_resources["Monitoring and Logs"]["Get measurement for host"].format(
            group_id=self.group_id,
            host=self.hostname,
            port=self.port,
            granularity=granularity,
            period=period,
            measurement=measurement
        )
        logger.info(f'The URI is.... {uri}')

        # Build the request
        return_val = atlas_obj.network.get(Settings.BASE_URL + uri)
        for each_response in return_val:
            for each_measurement in each_response.get("measurements"):
                measurement_obj = AtlasMeasurement(name=each_measurement.get('name'),
                                                   units=each_measurement.get('units', None),
                                                   period=period,
                                                   granularity=granularity)
                for each_and_every in each_measurement.get('dataPoints'):
                    measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

                yield measurement_obj


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

    def get_partitions(self, atlas_obj) -> Iterable[str]:
        """Returns names of all disks(partitions) configured on the Atlas Host
        Args:
            atlas_obj :

        Returns:
            Iterable[str]: A list of partition names.
        """
        uri = Settings.api_resources["Monitoring and Logs"]["Get Available Disks for Process"].format(
            group_id=self.group_id,
            host=self.hostname,
            port=self.port,
        )
        logger.info(f"The full URI being called is {Settings.BASE_URL + uri}")
        return_val = atlas_obj.network.get(Settings.BASE_URL + uri)
        for each_result in return_val:
            for each_partition in each_result.get("results"):
                partition_name: str = each_partition.get('partitionName', None)
                yield partition_name

    def get_measurements_for_disk(self, atlas_obj, partition_name: str,
                                  granularity: Optional[AtlasGranularities] = None,
                                  period: Optional[AtlasPeriods] = None, iterable: bool = True) -> \
            Iterable[Union[AtlasMeasurement, Any]]:
        """Returns All Metrics for a Hosts partition, for a given period and granularity.

        Uses default granularity and period if not passed.

        Args:
            iterable (bool): Defaults to true, if not true will return the raw response from API.
            partition_name: The Atlas partition name (commonly `data`)
            period (Optional[AtlasPeriods]):The period for the disk measurements
            granularity (Optional[AtlasGranularitues]): The granularity for the disk measurements.
            atlas_obj (atlasapi.atlas.Atlas): A configured Atlas instance to connect to the API with.

        Returns:
            List[str]: A list of partition names.
        """
        if period is None:
            period = AtlasPeriods.WEEKS_1
        logger.info(f'The period  is {period}')

        if granularity is None:
            granularity = AtlasGranularities.HOUR
        logger.info(f'The granularity is {granularity}')

        parameters = {'granularity': granularity, 'period': period}
        uri = Settings.api_resources["Monitoring and Logs"]["Get Measurements of a Disk for Process"].format(
            group_id=self.group_id,
            host=self.hostname,
            port=self.port,
            disk_name=partition_name,
        )
        logger.info(f"The full URI being called is {Settings.BASE_URL + uri}")
        logger.info(f"We will send the following parameters: {parameters}")
        return_val = atlas_obj.network.get(uri=Settings.BASE_URL + uri, params=parameters)
        measurement_obj = None
        for each_page in return_val:
            for each in each_page.get('measurements'):
                measurement_obj = AtlasMeasurement(name=each.get('name'),
                                                   period=period,
                                                   granularity=granularity,
                                                   units=each.get('units', None))
                for each_and_every in each.get('dataPoints'):
                    measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

                yield measurement_obj

    def data_partition_stats(self, atlas_obj, granularity: Optional[AtlasGranularities] = None,
                             period: Optional[AtlasPeriods] = None, ) -> Iterable[AtlasMeasurement]:
        """Returns disk measurements for the data partition of the host.

        Hard codes the name of the partition to `data` and returns all metrics.

        Args:
            period:
            atlas_obj: Instantiated Atlas instance to access the API
            granularity (Optional[AtlasGranularitues]): The granularity for the disk measurements.
            atlas_obj (atlasapi.atlas.Atlas): A configured Atlas instance to connect to the API with.

        Returns (Iterable[AtlasMeasurement]): A generator yielding AtlasMeasurements

        """
        return self.get_measurements_for_disk(atlas_obj=atlas_obj, partition_name='data', granularity=granularity,
                                              period=period)

    def get_databases(self, atlas_obj) -> Iterable[str]:
        """Returns all disks(partitions) configured on the Atlas Host

        Yields names of databases, and appends them to the databa

        Args:
            atlas_obj :

        Returns:
            List[str]: A list of database names.
        """
        uri = Settings.api_resources["Monitoring and Logs"]["Get Available Databases for Process"].format(
            group_id=self.group_id,
            host=self.hostname,
            port=self.port,
        )
        logger.info(f"The full URI being called is {Settings.BASE_URL + uri}")
        return_val = atlas_obj.network.get(Settings.BASE_URL + uri)
        for each_page in return_val:
            for each_database in each_page.get("results"):
                db_name = each_database.get('databaseName', None)
                yield db_name

    def get_measurements_for_database(self, atlas_obj, database_name: str,
                                      granularity: Optional[AtlasGranularities] = None,
                                      period: Optional[AtlasPeriods] = None) -> Iterable[AtlasMeasurement]:
        """Returns All Metrics for a database, for a given period and granularity.

        Uses default granularity and period if not passed.

        Args:
            database_name (str): The database name (local should always exist, and can be used for testing)
            period (Optional[AtlasPeriods]):The period for the disk measurements
            granularity (Optional[AtlasGranularitues]): The granularity for the disk measurements.
            atlas_obj (atlasapi.atlas.Atlas): A configured Atlas instance to connect to the API with.

        Returns:
           Iterable[Union[AtlasMeasurement]: Yields AtlasMeasirements .
        """
        if period is None:
            period = AtlasPeriods.WEEKS_1
        logger.info(f'The period is {period}')

        if granularity is None:
            granularity = AtlasGranularities.HOUR
        logger.info(f'The granularity is {granularity}')

        parameters = {'granularity': granularity, 'period': period}
        uri = Settings.api_resources["Monitoring and Logs"]["Get Measurements of a Database for Process"].format(
            group_id=self.group_id,
            host=self.hostname,
            port=self.port,
            database_name=database_name,
        )
        logger.info(f"The full URI being called is {Settings.BASE_URL + uri}")
        logger.info(f"We sent the following parameters: {parameters}")
        return_val = atlas_obj.network.get(Settings.BASE_URL + uri, params=parameters)
        measurement_obj = None
        for each_page in return_val:
            for each in each_page.get("measurements"):
                measurement_obj = AtlasMeasurement(name=each.get('name'),
                                                   period=period,
                                                   granularity=granularity,
                                                   units=each.get('units', None))
                for each_and_every in each.get('dataPoints'):
                    measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

                yield measurement_obj

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
        aws_iam_type (IAMType): AWS IAM method by which the database applies IAM credentials to authenticates the database
         user. Atlas defaults to NONE. (optional)

    Keyword Args:
        databaseName (str): Auth Database Name
    """

    def __init__(self, username: str, password: str = None,
                 aws_iam_type: Optional[IAMType] = None, databaseName=Settings.databaseName) -> None:
        self.username = username
        self.password = password
        self.aws_iam_type = aws_iam_type.value
        self.databaseName = databaseName
        self.roles = []

    def getSpecs(self) -> dict:
        """Get specs

        Returns:
            dict: Representation of the object
        """
        content = dict(databaseName=self.databaseName, roles=self.roles, username=self.username)
        if self.password:
            content["password"] = self.password
            content["awsIAMType"] = "NONE"
        elif self.aws_iam_type:
            content["awsIAMType"] = self.aws_iam_type
            content["databaseName"] = r"$external"

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

        TODO: Need to test if this works correctly, looks like their may be a type problem.
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
            collectionName (str):
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
