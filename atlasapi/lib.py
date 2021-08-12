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

from isodate import Duration, duration_isoformat, parse_datetime
from isodate.isoerror import ISO8601Error
from typing import Iterator
import logging
from enum import Enum
from datetime import datetime

logger = logging.getLogger('atlasapi.lib')


class AtlasLogNames(Enum):
    """
    The name of the log file that you want to retrieve:

    """
    MONGODB = "mongodb.gz"
    MONGOS = "mongos.gz"
    MONGOD_AUDIT = "mongodb-audit-log.gz"
    MONGOS_AUDIT = "mongos-audit-log.gz"


class LogLine(object):
    def __init__(self, raw_line):
        self.raw_line = raw_line
        try:
            raw_line_data = self.raw_line.rstrip().split(maxsplit=4)
            self.date: datetime = parse_datetime(raw_line_data[0])
            self.level: str = raw_line_data[1]
            self.facility: str = raw_line_data[2]
            self.user: str = raw_line_data[3].replace('[', '').replace(']', '')
            self.line: str = raw_line_data[-1]
            self.type: str = "Full"
        except IndexError:
            raw_line_data = raw_line.rstrip().split(maxsplit=1)
            self.date: datetime = parse_datetime(raw_line_data[0])
            self.line: str = raw_line_data[-1]
            self.type: str = "SHORT"
        except ISO8601Error:
            logger.error(f'Error Parsing line: {raw_line}')
            pass


class AtlasUnits(Enum):
    SCALAR_PER_SECOND = 'SCALAR_PER_SECOND'
    SCALAR = 'SCALAR'
    PERCENT = 'PERCENT'
    MILLISECONDS = 'MILLISECONDS'
    BYTES = 'BYTES'
    GIGABYTES = 'GIGABYTES'
    BYTES_PER_SECOND = 'BYTES_PER_SECOND'
    MEGABYTES_PER_SECOND = 'MEGABYTES_PER_SECOND'
    GIGABYTES_PER_HOUR = 'GIGABYTES_PER_HOUR'


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
    MINUTES_15 = duration_isoformat(Duration(minutes=15))
    HOURS_1 = duration_isoformat(Duration(hours=1))
    HOURS_8 = duration_isoformat(Duration(hours=8))
    HOURS_24 = duration_isoformat(Duration(hours=24))
    HOURS_48 = duration_isoformat(Duration(hours=48))
    WEEKS_1 = duration_isoformat(Duration(weeks=1))
    WEEKS_4 = duration_isoformat(Duration(weeks=4))
    MONTHS_1 = duration_isoformat(Duration(months=1))
    MONTHS_2 = duration_isoformat(Duration(months=2))
    YEARS_1 = duration_isoformat(Duration(years=1))
    YEARS_2 = duration_isoformat(Duration(years=2))


# noinspection PyCallByClass
class _GetAll(object):
    is_leaf = False

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


class _GetAllLeaf(_GetAll):
    is_leaf = True


class ProviderName(Enum):
    AWS = 'Amazon Web Services'
    GCP = 'Google Cloud Platform'
    AZURE = 'Microsoft Azure'
    TENANT = 'Shared Tier'


class MongoDBMajorVersion(Enum):
    v3_4 = '3.4'
    v3_6 = '3.6'
    v4_0 = '4.0'
    v4_2 = '4.2'
    v4_4 = '4.4'
    v5_0 = '5.0'
    vX_x = 'Unknown'


class ClusterType(Enum):
    """
    The types of clusteres available in Atlas.

    GEOSHARDED is a Global write cluster sharded by geo information.

    """
    REPLICASET = 'Replica Set'
    SHARDED = 'Sharded Cluster'
    SHARDEDCLUSTER = 'Sharded Cluster'
    GEOSHARDED = 'Global Cluster'