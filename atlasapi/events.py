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

from typing import NewType, List, Optional, Union, Dict
from dateutil.parser import parse
import logging
from datetime import datetime

from atlasapi.events_event_types import AtlasEventTypes
import ipaddress
from copy import copy

logger = logging.getLogger(name='Atlas_events')


class _AtlasBaseEvent(object):
    def __init__(self, value_dict: dict) -> None:
        self.created_date = None
        try:
            self.created_date = parse(value_dict.get("created", None))
        except ValueError as e:
            logger.warning("Could not parse datetime value for created_date: {}".format(e))
            pass
        self.event_type = AtlasEventTypes[value_dict.get('eventTypeName', 'UNKNOWN')]  # type: AtlasEventTypes
        self.group_id = value_dict.get('groupId', None)  # type: str
        self.id = value_dict.get('id', None)  # type: str
        self.is_global_admin = value_dict.get('isGlobalAdmin', False)  # type: bool
        self.links = value_dict.get('links', None)  # type: list
        self.event_dict = value_dict  # type: dict
        self.additional_data = value_dict.get('raw', None)

    def as_dict(self):
        original_dict = self.__dict__
        return_dict = copy(original_dict)
        del return_dict['event_dict']
        del return_dict['additional_data']
        return_dict['created_date'] = datetime.isoformat(self.created_date)
        return_dict['event_type'] = self.event_type.name
        return_dict['event_type_desc'] = self.event_type.value

        if return_dict.get('remote_address'):
            return_dict['remote_address'] = return_dict['remote_address'].__str__()
        return return_dict


class _AtlasUserBaseEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.user_id = value_dict.get('userId', None)  # type: str
        self.username = value_dict.get('username')  # type: str
        try:
            self.remote_address = ipaddress.ip_address(value_dict.get('remoteAddress', None))  # type: ipaddress
        except ValueError:
            logger.info('No IP address found')
            self.remote_address = None


class AtlasEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)


class AtlasCPSEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        """
        Atlas Events for Cloud Provider Snapshot related events.

        Contains extra data points directly related to CPS events. There
        !NOTE! The extra data points are extracted from the "raw" property which is not guaranteed to be stable.

        Args:
            value_dict: The original dict of values from the Atlas API
        """
        super().__init__(value_dict)
        if self.additional_data:
            self.snapshot_id: Optional[str] = self.additional_data.get('snapshotId', None)
            self.snapshot_completion_date: Optional[datetime] = None
            self.snapshot_scheduled_creation_date: Optional[datetime] = None
            self.cluster_name: str = self.additional_data.get('clusterName', None)
            self.cluster_id: str = self.additional_data.get('clusterId', None)
            snapshot_completion_date = None
            snapshot_scheduled_creation_date = None
            try:
                snapshot_completion_date = self.additional_data.get('snapshotCompletionDate', None)
                self.snapshot_completion_date: Optional[datetime] = parse(snapshot_completion_date)
            except (ValueError, TypeError, AttributeError):
                logger.debug(f'Could not parse a CPS snapshot completion date: {snapshot_completion_date}')
            try:
                snapshot_scheduled_creation_date = self.additional_data.get('snapshotScheduledCreationDate', None)
                self.snapshot_scheduled_creation_date: Optional[datetime] = parse(snapshot_scheduled_creation_date)
            except (ValueError, TypeError, AttributeError):
                logger.debug(
                    f'Could not parse a CPS snapshot scheduled creation date: {snapshot_scheduled_creation_date}')


class AtlasDataExplorerEvent(_AtlasUserBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.database = value_dict.get('database', None)  # type: str
        self.collection = value_dict.get('collection', None)  # type: str
        self.op_type = value_dict.get('opType', None)  # type: str


class AtlasClusterEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.replica_set_name = value_dict.get('replicaSetName', None)  # type: str
        self.cluster_name = value_dict.get('clusterName', None)  # type: str


class AtlasHostEvent(_AtlasBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.hostname = value_dict.get('hostname', None)  # type: str
        self.port = value_dict.get('port', None)  # type: int
        self.replica_set_name = value_dict.get('replicaSetName', None)  # type: str


class AtlasFeatureEvent(_AtlasUserBaseEvent):
    def __init__(self, value_dict: dict) -> None:
        super().__init__(value_dict)
        self.hostname = value_dict.get('hostname', None)  # type: str
        self.feature_name = value_dict.get('featureName', None)  # type: str


def atlas_event_factory(value_dict: dict) -> Union[
    AtlasEvent, AtlasDataExplorerEvent, AtlasClusterEvent, AtlasHostEvent, AtlasFeatureEvent, AtlasCPSEvent]:
    if 'CPS_' in value_dict.get("eventTypeName", None):
        return AtlasCPSEvent(value_dict=value_dict)
    elif value_dict.get("featureName", None):
        return AtlasFeatureEvent(value_dict=value_dict)
    elif value_dict.get("hostname", None):
        return AtlasHostEvent(value_dict=value_dict)

    elif value_dict.get("clusterName", None):
        return AtlasClusterEvent(value_dict=value_dict)

    elif value_dict.get("database", None):
        return AtlasDataExplorerEvent(value_dict=value_dict)


    else:
        return AtlasEvent(value_dict=value_dict)


ListOfEvents = NewType('ListOfEvents', List[Union[Dict, _AtlasBaseEvent]])
