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

from builtins import open
from builtins import str

from dateutil.parser import parse

from atlasapi.atlas_types import OptionalFloat
from atlasapi.lib import AtlasPeriods, AtlasGranularities, logger, _GetAll

from atlasapi.settings import Settings
from atlasapi.errors import ErrRole

from datetime import datetime
from enum import Enum
from dateutil import parser
from atlasapi.atlas_types import *
from typing import Optional, NewType, List, Any, Union, Iterable, BinaryIO, Tuple, Generator
from datetime import datetime
import isodate
from atlasapi.lib import AtlasGranularities, AtlasPeriods, AtlasLogNames
import logging
from future import standard_library
import humanfriendly as hf
from logging import Logger
from statistics import mean

standard_library.install_aliases()
logger: Logger = logging.getLogger('Atlas.specs')


# etc., as needed


def clean_list(data_list: list) -> list:
    """Returns a list with any none values removed

    Args:
        data_list (list): The list to be cleaned

    Returns (list): The list cleaned of None values.

    """
    return list(filter(None, data_list))


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


class StatisticalValues:
    def __init__(self, data_list: list):
        self.samples: int = len(clean_list(data_list))
        self.mean: float = float(mean(clean_list(data_list)))
        self.min: float = float(min(clean_list(data_list)))
        self.max: float = float(max(clean_list(data_list)))


class StatisticalValuesFriendly:
    def __init__(self, data_list: list, data_type: str = None) -> None:
        """Returns human readable values for stats

        Args:
            data_list:
            data_type: The datatype either bytes or number
        """
        if data_type is None:
            data_type = 'bytes'
        if data_type == 'bytes':
            self.mean: str = hf.format_size(mean(clean_list(data_list)))
            self.min: str = hf.format_size(min(clean_list(data_list)))
            self.max: str = hf.format_size(max(clean_list(data_list)))
        else:
            self.mean: str = hf.format_number(mean(clean_list(data_list)))
            self.min: str = hf.format_number(min(clean_list(data_list)))
            self.max: str = hf.format_number(max(clean_list(data_list)))


class AtlasMeasurementTypes(_GetAll):
    """
    Helper class for all available atlas measurements.

    All classes and embedded classes have a get_all class method that returns an iterator of all measurements
    and sub measurements.

    """
    connections = 'CONNECTIONS'

    class Asserts(_GetAll):
        regular = 'ASSERT_REGULAR'
        warning = 'ASSERT_WARNING'
        msg = 'ASSERT_MSG'
        user = 'ASSERT_USER'

    class Cache(_GetAll):
        bytes_read = 'CACHE_BYTES_READ_INTO'
        bytes_written = 'CACHE_BYTES_WRITTEN_FROM'
        dirty = 'CACHE_DIRTY_BYTES'
        used = 'CACHE_USED_BYTES'

    class Cursors(_GetAll):
        open = 'CURSORS_TOTAL_OPEN'
        timed_out = 'CURSORS_TOTAL_TIMED_OUT'

    class Db(_GetAll):
        storage = 'DB_STORAGE_TOTAL'
        data_size = 'DB_DATA_SIZE_TOTAL'

    class DocumentMetrics(_GetAll):
        returned = 'DOCUMENT_METRICS_RETURNED'
        inserted = 'DOCUMENT_METRICS_INSERTED'
        updated = 'DOCUMENT_METRICS_UPDATED'
        deleted = 'DOCUMENT_METRICS_DELETED'

    class ExtraInfo(_GetAll):
        page_faults = 'EXTRA_INFO_PAGE_FAULTS'

    class GlobalLockCurrentQueue(_GetAll):
        total = 'GLOBAL_LOCK_CURRENT_QUEUE_TOTAL'
        readers = 'GLOBAL_LOCK_CURRENT_QUEUE_READERS'
        writers = 'GLOBAL_LOCK_CURRENT_QUEUE_WRITERS'

    class Memory(_GetAll):
        resident = 'MEMORY_RESIDENT'
        virtual = 'MEMORY_VIRTUAL'
        mapped = 'MEMORY_MAPPED'

    class Network(_GetAll):
        bytes_id = 'NETWORK_BYTES_IN'  # initial typo, kept for backwards compatibility
        bytes_in = 'NETWORK_BYTES_IN'
        bytes_out = 'NETWORK_BYTES_OUT'
        num_requests = 'NETWORK_NUM_REQUESTS'

    class Opcounter(_GetAll):
        cmd = 'OPCOUNTER_CMD'
        query = 'OPCOUNTER_QUERY'
        update = 'OPCOUNTER_UPDATE'
        delete = 'OPCOUNTER_DELETE'
        getmore = 'OPCOUNTER_GETMORE'
        insert = 'OPCOUNTER_INSERT'

        class Repl(_GetAll):
            cmd = 'OPCOUNTER_REPL_CMD'
            update = 'OPCOUNTER_REPL_UPDATE'
            delete = 'OPCOUNTER_REPL_DELETE'
            insert = 'OPCOUNTER_REPL_INSERT'

    class Operations(_GetAll):
        scan_and_order = 'OPERATIONS_SCAN_AND_ORDER'

        class ExecutionTime(_GetAll):
            reads = 'OP_EXECUTION_TIME_READS'
            writes = 'OP_EXECUTION_TIME_WRITES'
            commands = 'OP_EXECUTION_TIME_COMMANDS'

    class Oplog(_GetAll):
        master_time = 'OPLOG_MASTER_TIME'
        rate = 'OPLOG_RATE_GB_PER_HOUR'

    class QueryExecutor(_GetAll):
        scanned = 'QUERY_EXECUTOR_SCANNED'
        scanned_objects = 'QUERY_EXECUTOR_SCANNED_OBJECTS'

    class QueryTargetingScanned(_GetAll):
        per_returned = 'QUERY_TARGETING_SCANNED_PER_RETURNED'
        objects_per_returned = 'QUERY_TARGETING_SCANNED_OBJECTS_PER_RETURNED'

    class TicketsAvailable(_GetAll):
        reads = 'TICKETS_AVAILABLE_READS'
        writes = 'TICKETS_AVAILABLE_WRITES'

    class CPU(_GetAll):
        class Process(_GetAll):
            user = 'PROCESS_CPU_USER'
            kernel = 'PROCESS_CPU_KERNEL'
            children_user = 'PROCESS_CPU_CHILDREN_USER'
            children_kernel = 'PROCESS_CPU_CHILDREN_KERNEL'

        class ProcessNormalized(_GetAll):
            user = 'PROCESS_NORMALIZED_CPU_USER'
            kernel = 'PROCESS_NORMALIZED_CPU_KERNEL'
            children_user = 'PROCESS_NORMALIZED_CPU_CHILDREN_USER'
            children_kernel = 'PROCESS_NORMALIZED_CPU_CHILDREN_KERNEL'

        class System(_GetAll):
            user = 'SYSTEM_CPU_USER'
            kernel = 'SYSTEM_CPU_KERNEL'
            nice = 'SYSTEM_CPU_NICE'
            iowait = 'SYSTEM_CPU_IOWAIT'
            irq = 'SYSTEM_CPU_IRQ'
            softirq = 'SYSTEM_CPU_SOFTIRQ'
            guest = 'SYSTEM_CPU_GUEST'
            steal = 'SYSTEM_CPU_STEAL'

        class SystemNormalized(_GetAll):
            user = 'SYSTEM_NORMALIZED_CPU_USER'
            kernel = 'SYSTEM_NORMALIZED_CPU_KERNEL'
            nice = 'SYSTEM_NORMALIZED_CPU_NICE'
            iowait = 'SYSTEM_NORMALIZED_CPU_IOWAIT'
            irq = 'SYSTEM_NORMALIZED_CPU_IRQ'
            softirq = 'SYSTEM_NORMALIZED_CPU_SOFTIRQ'
            guest = 'SYSTEM_NORMALIZED_CPU_GUEST'
            steal = 'SYSTEM_NORMALIZED_CPU_STEAL'


class AtlasMeasurementValue(object):
    def __init__(self, value_dict: dict):
        """
        Class for holding a measurement value
        :type value_dict: dict
        :param value_dict: An Atlas standard Measurement value dictionary.
        """
        timestamp: int = value_dict.get('timestamp', None)
        value: float = value_dict.get('value', None)
        try:
            self.timestamp: datetime = parse(timestamp)
        except (ValueError, TypeError):
            logger.warning('Could not parse "{}" as a datetime.')
            self.timestamp = None
        try:
            if value is None:
                self.value = None
            self.value: float = float(value)
        except ValueError as e:
            self.value = None
            logger.warning('Could not parse the metric value "{}". Error was {}'.format(value, e))
        except TypeError:
            logger.info('Value is none.')
            self.value = None

    # noinspection PyBroadException
    @property
    def value_int(self) -> Optional[int]:
        try:
            return int(self.value)
        except Exception as e:
            return None

    @property
    def value_float(self) -> Optional[float]:
        try:
            return float(self.value)
        except Exception:
            return None

    def as_dict(self) -> dict:
        return dict(timestamp=self.timestamp.__str__(), value=self.value, value_int=self.value_int,
                    value_float=self.value_float)

    @property
    def as_tuple(self) -> Tuple[datetime, OptionalFloat]:
        """
        Returns a MeasurementValue as a tuple, timestamp first.
        :rtype: Tuple[datetime,OptionalFloat]
        :return: A tuple with a datetime and a float
        """
        return self.timestamp, self.value


class AtlasMeasurement(object):
    """A point in time container for an Atlas measurement.

            For a certain period, granularity and measurementType holds a list fo measurementValues.

            Args:
                name (AtlasMeasurementTypes): The name of the measurement type
                period (AtlasPeriods): The period the measurement covers
                granularity (AtlasGranularities): The granularity used for the measurement
                measurements (List[AtlasMeasurementValue]): A list of the actual measurement values
            """

    def __init__(self, name: AtlasMeasurementTypes, period: AtlasPeriods,
                 granularity: AtlasGranularities, measurements: List[AtlasMeasurementValue] = None):
        if measurements is None:
            measurements = list()
        self.name: AtlasMeasurementTypes = name
        self.period: AtlasPeriods = period
        self.granularity: AtlasGranularities = granularity
        self._measurements: List[AtlasMeasurementValue] = measurements

    @property
    def measurements(self) -> Iterable[AtlasMeasurementValue]:
        """
        Getter for the measurements.

        Returns:
            Iterator[AtlasMeasurementValue]: An iterator containing values objects.
        """
        for item in self._measurements:
            yield item

    @measurements.setter
    def measurements(self, value):
        if type(value) == list:
            self._measurements.extend(value)
        else:
            self._measurements.append(value)

    @measurements.deleter
    def measurements(self):
        self._measurements = []

    def measurements_as_tuples(self):
        if isinstance(self._measurements[0], AtlasMeasurementValue):
            for item in self._measurements:
                yield item.as_tuple

    @property
    def date_start(self):
        """The date of the first measurement.

        Returns:
            datetime: The date of the first measurement.
        """
        seq = [x.timestamp for x in self._measurements]
        return min(seq)

    @property
    def date_end(self):
        """The date of the last measurement

        Returns:
            datetime: The date of the last measurement.

        """
        seq = [x.timestamp for x in self._measurements]
        return max(seq)

    @property
    def measurements_count(self):
        """The count of measurements

        Returns:
            int: The count of measurements in the set
        """
        return len(self._measurements)

    @property
    def as_dict(self):
        """Returns the measurement as a dict, including the computed properties.

        Returns:
            dict:
        """
        return dict(measurements=self._measurements, date_start=self.date_start, date_end=self.date_end, name=self.name,
                    period=self.period, granularity=self.granularity, measurements_count=self.measurements_count
                    )

    @property
    def measurement_stats(self) -> StatisticalValues:
        """Returns a statistical info for measurement data"""
        data_list = list()
        for each_measurement in self.measurements:
            data_list.append(each_measurement.value_float)
        return StatisticalValues(data_list=data_list)

    @property
    def measurement_stats_friendly_bytes(self) -> StatisticalValuesFriendly:
        """Returns  statistical info for measurement data in friendly bytes format"""
        data_list = list()
        for each_measurement in self.measurements:
            data_list.append(each_measurement.value_float)
        return StatisticalValuesFriendly(data_list=data_list)

    @property
    def measurement_stats_friendly_number(self) -> StatisticalValuesFriendly:
        """Returns  statistical info for measurement data in friendly bytes format"""
        data_list = list()
        for each_measurement in self.measurements:
            data_list.append(each_measurement.value_float)
        return StatisticalValuesFriendly(data_list=data_list, data_type='number')

    def __hash__(self):
        return hash(self.name + '-' + self.period)

    def __eq__(self, other):
        """
        Measurements are considered duplicate of name and period are the same
        :param other:
        :return:
        """
        if isinstance(other, AtlasMeasurement):
            return ((self.name == other.name) and (self.period == other.period))


ListOfAtlasMeasurementValues = NewType('ListOfAtlasMeasurementValues', List[Optional[AtlasMeasurementValue]])

OptionalAtlasMeasurement = NewType('OptionalAtlasMeasurement', Optional[AtlasMeasurement])


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
            measurements (Optional[List[AtlasMeasurement]]: Holds list of host Measurements
            cluster_name (str): The cluster name (taken from the hostname)
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
            except (ValueError, OverflowError):
                self.last_ping = data.get("lastPing", None)
            self.links: Optional[List[str]] = data.get("links", [])
            self.port: Optional[int] = data.get("port", None)
            self.replica_set_name: Optional[str] = data.get("replicaSetName", None)
            self.type: OptionalStr = ReplicaSetTypes[data.get("typeName", "NO_DATA")]
            self.measurements: Optional[List[AtlasMeasurement]] = []
            self.cluster_name: str = self.hostname_alias.split('-')[0]
            self.log_files: Optional[List[HostLogFile]] = None

    def get_measurement_for_host(self, atlas_obj, granularity: Optional[AtlasGranularities] = None,
                                 period: Optional[AtlasPeriods] = None,
                                 measurement: Optional[AtlasMeasurementTypes] = None,
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
        measurement_obj = None
        if iterable:
            measurements = return_val.get('measurements')
            measurements_count = len(measurements)
            logger.info('There are {} measurements.'.format(measurements_count))

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
