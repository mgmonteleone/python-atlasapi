from enum import Enum
from typing import List, NewType, Optional
from pprint import pprint
from datetime import datetime
import pytz

FORMAT = '%Y-%m-%dT%H:%M:%SZ'


# Enums
class VolumeTypes(Enum):
    STANDARD = "Standard"
    PROVISIONED = 'Provisioned'


class ClusterStates(Enum):
    IDLE = 'Idle'
    CREATING = 'Creating'
    UPDATING = 'Updating'
    DELETING = 'Deleting'
    DELETED = 'Deleted'
    REPAIRING = 'Repairing'
    UNKNOWN = 'Unknown'


class ClusterType(Enum):
    REPLICASET = 'Replica Set'
    SHARDED = 'Sharded Cluster'
    GEOSHARDED = 'Global Cluster'


class InstanceSizeName(Enum):
    M2 = 'M2'
    M5 = 'M5'
    M10 = '10'
    M20 = 'M20'
    M30 = 'M30'
    M40 = 'M40'
    R40 = 'R40'
    M40_NVME = 'M40 NVME'
    M50 = 'M50'
    R50 = 'R50'
    M50_NVME = 'M50 NVME'
    M60 = 'M60'
    R60 = 'R60'
    M60_NVME = 'M60 NVME'
    R80 = 'R80'
    M80_NVME = 'M80 NVME'
    M140 = 'M140'
    M200 = 'M200'
    M200_NVME = 'M200_NVME'
    M400 = 'M400'
    M300 = 'M300'
    R400 = 'R400'
    M400_NVME = 'M400_NVME'


class ProviderName(Enum):
    AWS = 'Amazon Web Services'
    GCP = 'Google Cloud Platform'
    AZURE = 'Microsoft Azure'


class MongoDBMajorVersion(Enum):
    v3_4 = '3.4'
    v3_6 = '3.6'
    v4_0 = '4.0'
    v4_2 = '4.2'
    vX_x = 'Unknown'


# Classes

class ReplicationSpecs(object):
    def __init__(self, id: Optional[str] = None,
                 num_shards: Optional[int] = None,
                 zone_name: Optional[str] = None,
                 regions_config: Optional[dict] = None):
        self.regions_config = regions_config
        self.zone_name = zone_name
        self.num_shards = num_shards
        self.id = id

    @classmethod
    def from_dict(cls, data_dict: dict):
        id = data_dict.get('id', None)
        regions_config = data_dict.get('regionsConfig', None)
        zone_name = data_dict.get('zoneName', None)
        num_shards = data_dict.get('numShards', None)
        return cls(id, num_shards, zone_name, regions_config)


class ProviderSettings(object):
    def __init__(self,
                 size: InstanceSizeName = InstanceSizeName.M10,
                 provider: ProviderName = ProviderName.AWS,
                 region: str = None,
                 autoScaling: Optional[dict] = None,
                 diskIOPS: int = None,
                 encryptEBSVolume: bool = True,
                 volumeType: VolumeTypes = VolumeTypes.STANDARD
                 ):
        self.volumeType = volumeType
        self.encryptEBSVolume = encryptEBSVolume
        self.diskIOPS = diskIOPS
        self.autoScaling = autoScaling
        self.instance_size_name: InstanceSizeName = size
        self.provider_name: ProviderName = provider
        self.region_name: str = region

    @classmethod
    def from_dict(cls, data_dict: dict):
        try:
            size = InstanceSizeName(data_dict.get('instanceSizeName', None))
        except ValueError:
            size = None
        try:
            provider = ProviderName(data_dict.get('providerName', None))
        except ValueError:
            provider = None
        region = data_dict.get('regionName', None)
        autoscaling = data_dict.get('autoscaling', None)
        diskIOPS = data_dict.get('diskIOPS', None)
        encryptEBSVolume = data_dict.get('encryptEBSVolume', None)
        volumeType = data_dict.get('volumeType', None)
        return cls(size, provider, region, autoscaling, diskIOPS, encryptEBSVolume, volumeType)


class ClusterConfig(object):
    def __init__(self, backup_enabled: bool = False,
                 cluster_type: ClusterType = ClusterType.REPLICASET,
                 disk_size_gb: int = 32,
                 name: str = None,
                 mongodb_major_version: MongoDBMajorVersion = MongoDBMajorVersion.v4_0,
                 mongodb_version: Optional[str] = None,
                 num_shards: int = 1,
                 mongo_uri: Optional[str] = None,
                 mongo_uri_updated: Optional[str] = None,
                 mongo_uri_with_options: Optional[str] = None,
                 paused: bool = False,
                 pit_enabled: bool = False,
                 replication_factor: Optional[int] = None,
                 state_name: Optional[ClusterStates] = None,
                 autoscaling: dict = {},
                 replication_specs: list = [],
                 srv_address: Optional[str] = None,
                 providerSettings: Optional[ProviderSettings] = None
                 ):
        self.providerSettings = providerSettings
        self.backup_enabled: bool = backup_enabled
        self.cluster_type: ClusterType = cluster_type
        self.disk_size_gb: int = disk_size_gb
        self.name: Optional[str] = name
        self.mongodb_major_version: MongoDBMajorVersion = mongodb_major_version
        self.mongodb_version: Optional[str] = mongodb_version
        self.num_shards: int = num_shards
        self.mongo_uri: Optional[str] = mongo_uri
        self.mongo_uri_updated: Optional[datetime] = mongo_uri_updated
        self.mongod_uri_with_options: Optional[str] = mongo_uri_with_options
        self.paused: bool = paused
        self.pit_enabled: bool = pit_enabled
        self.replication_factor: Optional[int] = replication_factor
        self.state_name: Optional[ClusterStates] = state_name
        self.autoscaling: dict = autoscaling
        self.replication_specs: list = replication_specs
        self.srv_address: Optional[str] = srv_address

    @classmethod
    def fill_from_dict(cls, data_dict: dict):
        replication_specs = data_dict.get('replicationSpecs', {})
        backup_enabled = data_dict.get('backupEnabled', None)
        disk_size_gb = data_dict.get('diskSizeGB', None)
        name = data_dict.get('name', None)
        num_shards = data_dict.get('numShards', 1)
        clusterType = data_dict.get('clusterType', None)
        cluster_type = ClusterType[clusterType]
        mongo_uri = data_dict.get('mongoURI', None)
        mongo_uri_with_options = data_dict.get('mongoURIWithOptions', None)
        try:
            mongo_uri_updated = datetime.strptime(data_dict.get('mongoURIUpdated', None), FORMAT).astimezone(
                tz=pytz.UTC)
        except ValueError:
            mongo_uri_updated = None
        try:
            mongodb_major_version = MongoDBMajorVersion(data_dict.get('mongoDBMajorVersion'))
        except ValueError as e:
            mongodb_major_version = MongoDBMajorVersion.vX_x
        mongodb_version = data_dict.get('mongoDBVersion', None)
        paused = data_dict.get('paused', False)
        pit_enabled = data_dict.get('pitEnabled', False)
        replication_factor = data_dict.get('replicationFactor', None)
        state_name = ClusterStates[data_dict.get('stateName', ClusterStates.UNKNOWN)]
        autoscaling = data_dict.get('autoScaling', {})

        if len(replication_specs) > 1:
            raise ValueError('We are limited to a single replication spec.')
        replication_specs = replication_specs[0]
        repl_spec_obj = ReplicationSpecs.from_dict(replication_specs)
        replication_specs = repl_spec_obj
        provider_settings_dict = data_dict.get('providerSettings',None)
        srv_address = data_dict.get('srvAddress',None)
        providerSettings = ProviderSettings.from_dict(provider_settings_dict)
        return cls(backup_enabled, cluster_type, disk_size_gb, name, mongodb_major_version, mongodb_version,
                   num_shards, mongo_uri, mongo_uri_updated, mongo_uri_with_options, paused, pit_enabled,
                   replication_factor, state_name, autoscaling, [replication_specs], srv_address,providerSettings)

    def as_dict(self):
        # TODO: Rename and clean up the return values to match original JS names
        return_dict = self.__dict__
        return_dict['clusterType'] = self.cluster_type.name
        return_dict['mongoDBMajorVersion'] = self.mongodb_major_version.value
        return_dict.__delitem__('mongodb_major_version')
        return_dict['replicationSpecs'] = [self.replication_specs[0].__dict__]
        return_dict.__delitem__('replication_specs')
        return_dict['stateName'] = self.state_name.name
        return_dict.__delitem__('state_name')
        return_dict['providerSettings'] = self.providerSettings.__dict__
        return_dict.__delitem__('replication_factor')  # THis has been deprecated, so removing from dict output
        return_dict['mongoDBVersion'] = self.mongodb_version
        return_dict.__delitem__('mongodb_version')
        return_dict['srvAddress'] = self.srv_address
        return_dict.__delitem__('srv_address')
        return return_dict
