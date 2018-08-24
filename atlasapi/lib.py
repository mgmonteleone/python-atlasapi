from isodate import Duration, duration_isoformat
from typing import Generator, Iterator

class AtlasGranularities(object):
    """Helper class to create ISO 8601 durations to pass to the API

    To add more possible granularities, add them here.

    """
    MINUTE = duration_isoformat(Duration(minutes=1))
    FIVE_MINUTE = duration_isoformat(Duration(minutes=5))
    HOUR = duration_isoformat(Duration(hours=1))
    DAY = duration_isoformat(Duration(days=1))


class AtlasPeriods(object):
    """Helper class to create ISO 8601 durations to send to the Atlas period parameter.

    To add more periods, add them here.
    """
    HOURS_1 = duration_isoformat(Duration(hours=1))
    HOURS_8 = duration_isoformat(Duration(hours=8))
    HOURS_24 = duration_isoformat(Duration(hours=24))
    HOURS_48 = duration_isoformat(Duration(hours=48))
    WEEKS_1 = duration_isoformat(Duration(weeks=1))
    MONTHS_1 = duration_isoformat(Duration(months=1))
    MONTHS_2 = duration_isoformat(Duration(months=2))
    YEARS_1 = duration_isoformat(Duration(years=1))
    YEARS_2 = duration_isoformat(Duration(years=2))


# noinspection PyCallByClass
class _GetAll(object):
    @classmethod
    def get_all(cls) -> Iterator[str]:
        out = cls.__dict__
        for item in out:
            if '_' not in item and not item[0].isupper():
                yield cls.__getattribute__(cls, item)
            elif '_' not in item and item[0].isupper():
                sub_out = cls.__getattribute__(cls, item).__dict__
                for sub_item in sub_out:
                    if '_' not in sub_item and not sub_item[0].isupper():
                        yield cls.__getattribute__(cls, item).__dict__.get(sub_item)
                    if '_' not in sub_item and sub_item[0].isupper():
                        sub_sub_out = cls.__getattribute__(cls, item).__dict__.get(sub_item).__dict__
                        for sub_sub_item in sub_sub_out:
                            if '_' not in sub_sub_item and not sub_sub_item[0].isupper():
                                yield sub_sub_out.get(sub_sub_item)


class AtlasMeasurements(_GetAll):
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
        dirty = 'CACHE_USAGE_DIRTY'
        used = 'CACHE_USAGE_USED'

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

        class ExcecutionTime(_GetAll):
            reads = 'OP_EXECUTION_TIME_READS'
            writes = 'OP_EXECUTION_TIME_WRITES'
            commands = 'OP_EXECUTION_TIME_COMMANDS'

    class Oplog(_GetAll):
        master_time = 'OPLOG_MASTER_TIME'
        rate = 'OPLOG_RATE_GB_PER_HOUR'

    class QueryExceutor(_GetAll):
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


