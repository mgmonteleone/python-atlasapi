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

from datetime import datetime
from typing import Tuple, NewType, List, Optional

from dateutil.parser import parse

from atlasapi.atlas_types import OptionalFloat
from atlasapi.lib import _GetAll, logger


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
        bytes_id = 'NETWORK_BYTES_IN'
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
    def __init__(self, value_dict):
        """
        Class for holding a measurement value
        :type value_dict: dict
        :param value_dict: An Atlas standard Measurement value dictionary.
        """
        timestamp = value_dict.get('timestamp', None)
        value = value_dict.get('value', None)
        try:
            self.timestamp = parse(timestamp)
        except (ValueError, TypeError):
            logger.warning('Could not parse "{}" as a datetime.')
            self.timestamp = None
        try:
            if value is None:
                self.value = None
            self.value = float(value)
        except ValueError as e:
            self.value = None
            logger.warning('Could not parse the metric value "{}". Error was {}'.format(value, e))
        except TypeError:
            logger.info('Value is none.')
            self.value = None

    @property
    def value_int(self):
        try:
            return int(self.value)
        except Exception:
            return None

    @property
    def value_float(self):
        try:
            return float(self.value)
        except Exception:
            return None

    def as_dict(self):
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


ListOfAtlasMeasurementValues = NewType('ListOfAtlasMeasurementValues', List[Optional[AtlasMeasurementValue]])


class AtlasMeasurement(object):
    """A point in time container for an Atlas measurement.

            For a certain period, granularity and measurementType hoslds a list fo measurementValues.

            Args:
                name (AtlasMeasurementTypes): The name of the measurement type
                period (AtlasPeriods): The period the measurement covers
                granularity (AtlasGranularities): The granularity used for the measurement
                measurements (List[AtlasMeasurementValue]): A list of the actual measurement values
            """
    def __init__(self, name, period, granularity, measurements=list()):
        self.name = name
        self.period = period
        self.granularity = granularity
        self._measurements = measurements

    @property
    def measurements(self):
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

    def __hash__(self):
        return hash(self.name+'-'+self.period)

    def __eq__(self, other):
        """
        Measurements are considered duplicate of name and period are the same
        :param other:
        :return:
        """
        if isinstance(other, AtlasMeasurement):
            return  ((self.name == other.name) and (self.period == other.period))

OptionalAtlasMeasurement = NewType('OptionalAtlasMeasurement', Optional[AtlasMeasurement])