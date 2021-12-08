# Copyright (c) 2021 Matthew G. Monteleone
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
Cloud Backups Module

Provides access to Cloud Backups and Cloud backup restore endpoints
"""

from enum import Enum
from typing import List, NewType, Optional
from datetime import datetime
from atlasapi.lib import ProviderName, ClusterType
from dateutil.parser import parse
from pprint import pprint
from distutils.util import strtobool
import logging

logger = logging.getLogger(name='Atlas_cloud_backup')


def try_date(str_in: str) -> Optional[datetime]:
    try:
        datetime_out = parse(str_in)
    except (ValueError, TypeError, AttributeError):
        logger.debug(f'Could not parse a date from : {str_in}')
        datetime_out = None
    return datetime_out


def try_bool(str_in: str) -> bool:
    if type(str_in) != bool:
        try:
            bool_out = strtobool(str_in)
        except (ValueError, TypeError, AttributeError):
            logger.debug(f'Could not parse a bool from : {str_in}')
            bool_out = False
    else:
        bool_out = str_in
    return bool_out


class SnapshotType(Enum):
    ONDEMAND = "On Demand"
    SCHEDULED = "Scheduled"
    FALLBACK = "Fallback"


class SnapshotStatus(Enum):
    QUEUED = "Queued"
    INPROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class DeliveryType(Enum):
    automated = "Automated restore to Atlas cluster"
    download = "manual download of archived data directory"
    pointInTime = "Automated point in time restore to Atlas Cluster"


class SnapshotRestore(object):
    def __init__(self, delivery_type: DeliveryType,
                 snapshot_id: str,
                 target_cluster_name: str = None,
                 target_group_id: str = None):
        self.deliveryType = delivery_type
        self.snapshot_id = snapshot_id
        self.target_cluster_name = target_cluster_name
        self.target_group_id = target_group_id

    @property
    def as_dict(self) -> dict:
        return dict(
            deliveryType=self.deliveryType.name,
            snapshotId=self.snapshot_id,
            targetClusterName=self.target_cluster_name,
            targetGroupId=self.target_group_id
        )


class SnapshotRestoreResponse(SnapshotRestore):
    def __init__(self, restore_id: str, delivery_type: DeliveryType, snapshot_id: str, target_cluster_name: str,
                 target_group_id: str, cancelled: bool = False,
                 created_at: datetime = None, expired: bool = False, expires_at: datetime = None,
                 finished_at: datetime = None, links: list = None, snapshot_timestamp: datetime = None,
                 target_deployment_item_name: str = None,
                 delivery_url: str = None):
        super().__init__(delivery_type, snapshot_id, target_cluster_name, target_group_id)
        self.delivery_url = delivery_url
        self.target_deployment_item_name = target_deployment_item_name
        self.snapshot_timestamp = snapshot_timestamp
        self.links = links
        self.finished_at = finished_at
        self.expires_at = expires_at
        self.expired = expired
        self.created_at = created_at
        self.cancelled = cancelled
        self.restore_id = restore_id

    @classmethod
    def from_dict(cls, data_dict):
        restore_id = data_dict.get('id')
        snapshot_id = data_dict.get('snapshotId')
        try:
            delivery_type = DeliveryType[data_dict.get('deliveryType')]
        except KeyError:
            logger.warning(f'Got an unmapped deliveryType : {data_dict.get("deliveryType")}.')
            delivery_type = None
        target_cluster_name = data_dict.get('targetClusterName')
        target_group_id = data_dict.get('targetGroupId')
        cancelled = try_bool(data_dict.get('cancelled'))
        created_at = try_date(data_dict.get('createdAt')) # Does not appear to be retunred at all, potential docs issue?
        expired = try_bool(data_dict.get('expired'))
        expires_at = try_date(data_dict.get('expiresAt')) # Does not appear to be retunred at all, potential docs issue?
        finished_at = try_date(data_dict.get('finishedAt')) # Does not appear to be retunred at all, potential docs issue?
        links = data_dict.get('links')
        snapshot_timestamp = try_date(data_dict.get('timestamp'))
        target_deployment_item_name=data_dict.get('targetDeploymentItemName') # missing in documentation TODO: File docs ticket.
        delivery_url = data_dict.get('deliveryUrl',None) # missing in documentation TODO: File docs ticket

        return cls(restore_id=restore_id,
                   delivery_type=delivery_type,
                   snapshot_id=snapshot_id,
                   target_cluster_name=target_cluster_name,
                   target_group_id=target_group_id,
                   cancelled=cancelled,
                   created_at=created_at,
                   expired=expired,
                   expires_at=expires_at,
                   finished_at=finished_at,
                   links=links,
                   snapshot_timestamp=snapshot_timestamp,
                   target_deployment_item_name=target_deployment_item_name,
                   delivery_url=delivery_url)


class CloudBackupRequest(object):
    def __init__(self, cluster_name: str, retention_days: int = 1, description: str = 'Created by pyAtlasAPI') -> None:
        self.description = description
        self.retentionInDays = retention_days
        self.cluster_name = cluster_name

    @property
    def as_dict(self):
        return dict(description=self.description, retentionInDays=self.retentionInDays)


class CloudBackupSnapshot(object):
    def __init__(self, id: Optional[str] = None,
                 cloud_provider: Optional[ProviderName] = None,
                 created_at: Optional[datetime] = None,
                 description: Optional[str] = None,
                 expires_at: Optional[datetime] = None,
                 links: Optional[List] = None,
                 masterkey_uuid: Optional[str] = None,
                 members: Optional[list] = None,
                 mongod_version: Optional[str] = None,
                 replica_set_name: Optional[str] = None,
                 snapshot_ids: Optional[list] = None,
                 snapshot_type: Optional[SnapshotType] = None,
                 status: Optional[SnapshotStatus] = None,
                 storage_size_bytes: Optional[int] = None,
                 type: Optional[ClusterType] = None):
        """
        Details of a Cloud Provider Snapshot.

        Args:
            id: Unique identifier of the snapshot.
            cloud_provider: Cloud provider that stores this snapshot. Atlas returns this parameter
            when "type": "replicaSet".
            created_at:
            description: Description of the snapshot. Atlas returns this parameter when "status": "onDemand".
            expires_at:
            links: One or more links to sub-resources and/or related resources. The relations between URLs are
                   explained in the Web Linking Specification
            masterkey_uuid: Unique identifier of the AWS KMS Customer Master Key used to encrypt the snapshot.
                            Atlas returns this value for clusters using Encryption at Rest via Customer KMS.
            members: List of snapshots and the cloud provider where the snapshots are stored.
                     Atlas returns this parameter when "type": "shardedCluster".
            mongod_version:
            replica_set_name: Label given to the replica set from which Atlas took this snapshot.
                              Atlas returns this parameter when "type": "replicaSet".
                              snapshot_ids: Unique identifiers of the snapshots created for the shards and config server
                              for a sharded cluster. Atlas returns this parameter when "type": "shardedCluster".
                              These identifiers should match those given in the members[n].id parameters.
                              This allows you to map a snapshot to its shard or config server name.
            snapshot_type: Type of snapshot. Atlas can return onDemand or scheduled.
            status: Current status of the snapshot. Atlas can return one of the following values:
                    (queued, inProgress, completed, failed)
            storage_size_bytes:
            type: Type of cluster. Atlas can return replicaSet or shardedCluster.


        """
        self.type: Optional[ClusterType] = type
        self.storage_size_bytes: Optional[int] = storage_size_bytes
        self.status: Optional[SnapshotStatus] = status
        self.snapshot_type: Optional[SnapshotType] = snapshot_type
        self.snapshot_ids: Optional[list] = snapshot_ids
        self.replica_set_name: Optional[str] = replica_set_name
        self.mongod_version: Optional[str] = mongod_version
        self.members: Optional[list] = members
        self.masterkey_uuid: Optional[str] = masterkey_uuid
        self.links: Optional[list] = links
        self.expires_at: Optional[datetime] = expires_at
        self.description: Optional[str] = description
        self.created_at: Optional[datetime] = created_at
        self.cloud_provider: Optional[ProviderName] = cloud_provider
        self.id: Optional[str] = id

    @classmethod
    def from_dict(cls, data_dict: dict):
        id = data_dict.get('id', None)
        try:
            cloud_provider = ProviderName[data_dict.get('cloudProvider')]
        except KeyError:
            cloud_provider = ProviderName.TENANT
        created_at = try_date(data_dict.get('createdAt'))
        expires_at = try_date(data_dict.get('expiresAt'))
        description = data_dict.get('description')
        snapshot_type = SnapshotType[data_dict.get('snapshotType').upper()]
        cluster_type = ClusterType[data_dict.get('type').upper()]
        snapshot_status = SnapshotStatus[data_dict.get('status').upper()]
        storage_size_bytes = data_dict.get('storageSizeBytes')
        replica_set_name = data_dict.get('replicaSetName')
        links = data_dict.get('links')
        masterkey = data_dict.get('masterKeyUUID')
        members = data_dict.get('members')
        mongod_version = data_dict.get('mongodVersion')
        snapshot_ids = data_dict.get('snapshotIds')
        return cls(id=id,
                   cloud_provider=cloud_provider,
                   created_at=created_at,
                   expires_at=expires_at,
                   description=description,
                   snapshot_type=snapshot_type,
                   type=cluster_type,
                   status=snapshot_status,
                   storage_size_bytes=storage_size_bytes,
                   replica_set_name=replica_set_name,
                   links=links,
                   masterkey_uuid=masterkey,
                   members=members,
                   mongod_version=mongod_version,
                   snapshot_ids=snapshot_ids
                   )
