from __future__ import division, absolute_import, print_function, unicode_literals

from datetime import datetime
from statistics import mean, StatisticsError
from typing import Optional, Tuple, List, Iterable, NewType
import logging
import humanfriendly as hf
from dateutil.parser import parse

from atlasapi.atlas_types import OptionalFloat
from atlasapi.lib import _GetAll, AtlasPeriods, AtlasGranularities

logger: logging.Logger = logging.getLogger('Atlas.measurements')


class StatisticalValues:
    def __init__(self, data_list: list):
        try:
            self.samples: int = len(clean_list(data_list))
            self.mean: float = float(mean(clean_list(data_list)))
            self.min: float = float(min(clean_list(data_list)))
            self.max: float = float(max(clean_list(data_list)))
        except StatisticsError:
            logger.warning('Could not compute statistical values.')
            self.samples: int = 0
            self.mean: float = 0
            self.min: float = 0
            self.max: float = 0


class StatisticalValuesFriendly:
    def __init__(self, data_list: list, data_type: str = None) -> None:
        """Returns human-readable values for stats

        Args:
            data_list:
            data_type: The datatype either bytes or number
        """
        try:
            if data_type is None:
                data_type = 'SCALAR_PER_SECOND'
            if data_type == 'BYTES':
                self.mean: str = hf.format_size(mean(clean_list(data_list)))
                self.min: str = hf.format_size(min(clean_list(data_list)))
                self.max: str = hf.format_size(max(clean_list(data_list)))
            elif data_type == 'SCALAR':
                self.mean: str = hf.format_number(mean(clean_list(data_list)))
                self.min: str = hf.format_number(min(clean_list(data_list)))
                self.max: str = hf.format_number(max(clean_list(data_list)))
            else:
                self.mean: str = hf.format_number(mean(clean_list(data_list)))
                self.min: str = hf.format_number(min(clean_list(data_list)))
                self.max: str = hf.format_number(max(clean_list(data_list)))

        except StatisticsError:
            logger.warning('Could not compute statistical values.')
            self.mean: str = 'No Value'
            self.min: str = 'No value'
            self.max: str = 'No value'


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
        writes = 'TICKETS_AVAILABLE_WRITE'

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

    class Disk(_GetAll):
        class IOPS(_GetAll):
            read = 'DISK_PARTITION_IOPS_READ'
            read_max = 'MAX_DISK_PARTITION_IOPS_READ'
            write = 'DISK_PARTITION_IOPS_WRITE'
            write_max = 'MAX_DISK_PARTITION_IOPS_WRITE'
            total = 'DISK_PARTITION_IOPS_TOTAL'
            total_max = 'MAX_DISK_PARTITION_IOPS_TOTAL'

        class Util(_GetAll):
            util = 'DISK_PARTITION_UTILIZATION'
            util_max = 'MAX_DISK_PARTITION_UTILIZATION'

        class Latency(_GetAll):
            read = 'DISK_PARTITION_LATENCY_READ'
            read_max = 'MAX_DISK_PARTITION_LATENCY_READ'
            write = 'DISK_PARTITION_LATENCY_WRITE'
            write_max = 'MAX_DISK_PARTITION_LATENCY_WRITE'

        class Free(_GetAll):
            space_free = 'DISK_PARTITION_SPACE_FREE'
            space_free_max = 'MAX_DISK_PARTITION_SPACE_FREE'
            used = 'DISK_PARTITION_SPACE_USED'
            used_max = 'MAX_DISK_PARTITION_SPACE_USED'
            percent_fee = 'DISK_PARTITION_SPACE_PERCENT_FREE'
            percent_free_max = 'MAX_DISK_PARTITION_SPACE_PERCENT_FREE'
            percent_used = 'DISK_PARTITION_SPACE_PERCENT_USED'
            percent_used_max = 'MAX_DISK_PARTITION_SPACE_PERCENT_USED'

    class Namespaces(_GetAll):
        """Metrics regarding namespaces (databases) on each host.

        As found in dbstats (https://www.mongodb.com/docs/manual/reference/command/dbStats/)
            """
        object_size = 'DATABASE_AVERAGE_OBJECT_SIZE' # dbStats.avgObjSize Average size of each document in bytes. This is the dataSize divided by the number of documents. The scale argument does not affect the avgObjSize value.
        collection_count = 'DATABASE_COLLECTION_COUNT'
        data_size = 'DATABASE_DATA_SIZE' # Total size of the uncompressed data held in the database. The dataSize decreases when you remove documents.
        storage_size = 'DATABASE_STORAGE_SIZE' # Sum of the space allocated to all collections in the database for document storage, including free space. storageSize does not include space allocated to indexes. See indexSize for the total index size.
        index_size = 'DATABASE_INDEX_SIZE' # Sum of the space allocated to all indexes in the database, including free index space.
        index_count = 'DATABASE_INDEX_COUNT'
        extent_count = 'DATABASE_EXTENT_COUNT' # ?
        object_count = 'DATABASE_OBJECT_COUNT' # Number of objects (specifically, documents) in the database across all collections.
        view_count = 'DATABASE_VIEW_COUNT'


# noinspection PyBroadException
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
                units (Text): Descriptive text of units used.
                period (AtlasPeriods): The period the measurement covers
                granularity (AtlasGranularities): The granularity used for the measurement
                measurements (List[AtlasMeasurementValue]): A list of the actual measurement values
            """

    def __init__(self, name: AtlasMeasurementTypes, period: AtlasPeriods,
                 granularity: AtlasGranularities, units: str = None, measurements: List[AtlasMeasurementValue] = None):
        if measurements is None:
            measurements = list()
        self.name: AtlasMeasurementTypes = name
        self.units: str = units
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
                    units=self.units, period=self.period, granularity=self.granularity,
                    measurements_count=self.measurements_count
                    )

    @property
    def measurement_stats(self) -> StatisticalValues:
        """Returns a statistical info for measurement data"""
        data_list = list()
        for each_measurement in self.measurements:
            data_list.append(each_measurement.value_float)
        return StatisticalValues(data_list=data_list)

    @property
    def measurement_stats_friendly(self) -> StatisticalValuesFriendly:
        """Returns  statistical info for measurement data in friendly bytes format"""
        data_list = list()
        for each_measurement in self.measurements:
            data_list.append(each_measurement.value_float)
        return StatisticalValuesFriendly(data_list=data_list, data_type=self.units)

    def __hash__(self):
        return hash(self.name + '-' + self.period)

    def __eq__(self, other):
        """
        Measurements are considered duplicate of name and period are the same
        :param other:
        :return:
        """
        if isinstance(other, AtlasMeasurement):
            return (self.name == other.name) and (self.period == other.period)


ListOfAtlasMeasurementValues = NewType('ListOfAtlasMeasurementValues', List[Optional[AtlasMeasurementValue]])
OptionalAtlasMeasurement = NewType('OptionalAtlasMeasurement', Optional[AtlasMeasurement])


def clean_list(data_list: list) -> list:
    """Returns a list with any none values removed

    Args:
        data_list (list): The list to be cleaned

    Returns (list): The list cleaned of None values.

    """
    return list(filter(None, data_list))
