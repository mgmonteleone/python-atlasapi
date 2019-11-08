from enum import Enum
from typing import List, NewType, Optional
from pprint import pprint
from datetime import datetime
import pytz
import uuid
import copy

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
    M10 = 'M10'
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

class RegionConfig(object):
    def __init__(self,
                 electable_node_count: int = 3,
                 priority: int = 7,
                 read_only_node_count: int = 0,
                 analytics_node_count: int = 0):
        self.analyticsNodes = analytics_node_count
        self.electableNodes = electable_node_count
        self.priority = priority
        self.readOnlyNodes = read_only_node_count


class ReplicationSpecs(object):
    def __init__(self, id: Optional[str] = uuid.uuid4().__str__(),
                 num_shards: Optional[int] = 1,
                 zone_name: Optional[str] = None,
                 regions_config: Optional[dict] = None):
        """
        Configuration of each region in the cluster. Each element in this document represents a region where Atlas deploys your cluster.

        NOTE: A ReplicationSpecs object is found in Atlas replicationSpecs

        :param id:
        :param num_shards:
        :param zone_name:
        :param regions_config:
        """
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

    def as_dict(self):
        return_dict = self.__dict__
        return_dict['numShards'] = self.num_shards
        return_dict.__delitem__('num_shards')
        return_dict['regionsConfig'] = self.regions_config
        return_dict.__delitem__('regions_config')
        if self.zone_name is not None:
            return_dict['zoneName'] = self.zone_name
        return_dict.__delitem__('zone_name')

        return return_dict

    def as_create_dict(self):
        out_dict = self.as_dict()
        out_dict.__delitem__('id')

        return out_dict


class ProviderSettings(object):
    def __init__(self,
                 size: InstanceSizeName = InstanceSizeName.M10,
                 provider: ProviderName = ProviderName.AWS,
                 region: str = 'US_WEST_1',
                 autoScaling: Optional[dict] = None,
                 diskIOPS: int = None,
                 encryptEBSVolume: bool = True,
                 volumeType: VolumeTypes = VolumeTypes.STANDARD
                 ):
        """
        Configuration for the provisioned servers on which MongoDB runs.


        :param size: Name of the cluster tier used for the Atlas cluster.
        :param provider: Cloud service provider on which the servers are provisioned.
        :param region: Physical location of your MongoDB cluster. The region you choose can affect network latency for
                        clients accessing your databases.
        :param autoScaling: Contains the compute field which specifies the range of instance sizes to which your cluster
                can scale.
        :param diskIOPS: Maximum input/output operations per second (IOPS) the system can perform.
        :param encryptEBSVolume: AWS only. If enabled, the Amazon EBS encryption feature encrypts the server’s root
                volume for both data at rest within the volume and for data moving between the volume and the cluster.
        :param volumeType: The type of AWS volume.
        """
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
            size = InstanceSizeName[data_dict.get('instanceSizeName', None)]
        except ValueError:
            size = None
        try:
            provider = ProviderName[data_dict.get('providerName', None)]
        except ValueError:
            provider = None
        region = data_dict.get('regionName', None)
        autoscaling = data_dict.get('autoScaling', None)
        diskIOPS = data_dict.get('diskIOPS', None)
        encryptEBSVolume = data_dict.get('encryptEBSVolume', None)
        volumeType = data_dict.get('volumeType', None)
        return cls(size, provider, region, autoscaling, diskIOPS, encryptEBSVolume, volumeType)

    def as_dict(self) -> dict:
        out_dict = self.__dict__
        out_dict['instanceSizeName'] = self.instance_size_name.name
        out_dict['providerName'] = self.provider_name.name
        out_dict['volumeType'] = self.volumeType
        out_dict['regionName'] = self.region_name
        del out_dict['provider_name']
        del out_dict['instance_size_name']
        del out_dict['region_name']

        return out_dict


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
                 autoscaling: dict = None,
                 replication_specs: ReplicationSpecs = None,
                 srv_address: Optional[str] = None,
                 providerSettings: Optional[ProviderSettings] = None,
                 links: list = None
                 ) -> None:
        """
        Stores the Atlas Cluster Config, is sent back to the API for any reconfiguations.

        https://docs.atlas.mongodb.com/reference/api/clusters-get-one/#http-response-elements

        :param backup_enabled:
        :param cluster_type:
        :param disk_size_gb:
        :param name:
        :param mongodb_major_version:
        :param mongodb_version:
        :param num_shards:
        :param mongo_uri:
        :param mongo_uri_updated:
        :param mongo_uri_with_options:
        :param paused:
        :param pit_enabled:
        :param replication_factor:
        :param state_name:
        :param autoscaling:
        :param replication_specs:
        :param srv_address:
        :param providerSettings:
        :param links:
        """
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
        if type(replication_specs) == list:
            self.replication_specs: List[ReplicationSpecs] = replication_specs
        else:
            self.replication_specs: List[ReplicationSpecs] = [replication_specs]
        self.links: Optional[list] = links
        self.srv_address: str = srv_address

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
        provider_settings_dict = data_dict.get('providerSettings', None)
        srv_address = data_dict.get('srvAddress', None)
        providerSettings = ProviderSettings.from_dict(provider_settings_dict)
        links = data_dict.get('links', [])
        return cls(backup_enabled, cluster_type, disk_size_gb, name, mongodb_major_version, mongodb_version,
                   num_shards, mongo_uri, mongo_uri_updated, mongo_uri_with_options, paused, pit_enabled,
                   replication_factor, state_name, autoscaling, replication_specs, srv_address, providerSettings, links)

    def as_dict(self) -> dict:
        return_dict = self.__dict__
        try:
            return_dict['clusterType'] = self.cluster_type.name
            return_dict.__delitem__('cluster_type')
            return_dict['mongoDBMajorVersion'] = self.mongodb_major_version.value
            return_dict.__delitem__('mongodb_major_version')
            return_dict['replicationSpecs'] = [self.replication_specs[0].as_dict()]
            return_dict.__delitem__('replication_specs')

        except (KeyError, AttributeError):
            pass

        try:
            return_dict['stateName'] = self.state_name.name
        except AttributeError:
            pass
        try:
            return_dict.__delitem__('state_name')
        except KeyError:
            pass
        try:
            return_dict['providerSettings'] = self.providerSettings.as_dict()
        except AttributeError:
            return_dict['providerSettings'] = self.providerSettings
        try:
            return_dict.__delitem__('replication_factor')  # THis has been deprecated, so removing from dict output
            return_dict['mongoDBVersion'] = self.mongodb_version
            return_dict.__delitem__('mongodb_version')
            return_dict['srvAddress'] = self.srv_address
            return_dict.__delitem__('srv_address')
            return_dict['mongoURI'] = self.mongo_uri
            return_dict.__delitem__('mongo_uri')
            return_dict['mongoURIWithOptions'] = self.mongod_uri_with_options
            return_dict.__delitem__('mongod_uri_with_options')
            return_dict['diskSizeGB'] = self.disk_size_gb
            return_dict.__delitem__('disk_size_gb')
            return_dict['pitEnabled'] = self.pit_enabled
            return_dict.__delitem__('pit_enabled')
            return_dict['numShards'] = self.num_shards
            return_dict.__delitem__('num_shards')
            return_dict['mongoURIUpdated'] = self.mongo_uri_updated
            return_dict.__delitem__('mongo_uri_updated')
            return_dict['backupEnabled'] = self.backup_enabled
            return_dict.__delitem__('backup_enabled')
        except KeyError:
            pass

        return return_dict

    def as_create_dict(self) -> dict:
        """
        Returns the config object in a format acceptable for the POST (create) endpoint.

        Removes properties which are read-only.

        TODO: Refactor to identify which properties are RO in the spec, and automatically loop through and remove.

        :return: dict: A dict containing a valid create object for the POST endpoint.
        """
        out_dict = self.as_dict()
        try:
            out_dict.pop('numShards', None)
            out_dict.pop('mongoURI', None)
            out_dict.pop('mongoDBVersion', None)
            out_dict.pop('mongoURIUpdated', None)
            out_dict.pop('mongoURIWithOptions', None)
            out_dict.pop('paused', None)
            out_dict.pop('srvAddress', None)
            out_dict.pop('links', None)
            out_dict.pop('state_name', None)
        except KeyError:
            pass
        try:
            out_dict['replicationSpecs'][0].__delitem__('id')
        except KeyError:
            pass
        return out_dict

    def as_modify_dict(self) -> dict:
        """
        Returns the config object in a format acceptable for the PATCH (modify) endpoint.

        Removes properties which are read-only.

        TODO: Refactor to identify which properties are RO in the spec, and automatically loop through and remove.

        :return: dict: A dict containing a valid create object for the POST endpoint.
        """
        out_dict = self.as_dict()
        out_dict.pop('stateName', None)
        out_dict.pop('numShards', None)
        out_dict.pop('mongoURI', None)
        out_dict.pop('mongoDBVersion', None)
        out_dict.pop('mongoURIUpdated', None)
        out_dict.pop('mongoURIWithOptions', None)
        out_dict.pop('paused', None)
        out_dict.pop('srvAddress', None)
        out_dict.pop('links', None)
        out_dict.pop('state_name', None)

        return out_dict


class ShardedClusterConfig(ClusterConfig):
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
                 providerSettings: Optional[ProviderSettings] = None):
        super().__init__(backup_enabled, cluster_type, disk_size_gb, name, mongodb_major_version, mongodb_version,
                         num_shards, mongo_uri, mongo_uri_updated, mongo_uri_with_options, paused, pit_enabled,
                         replication_factor, state_name, autoscaling, [replication_specs], srv_address,
                         providerSettings)

    def as_dict(self) -> dict:
        return_dict = self.__dict__
        return_dict['clusterType'] = self.cluster_type.name
        return_dict.__delitem__('cluster_type')
        return_dict['mongoDBMajorVersion'] = self.mongodb_major_version.value
        return_dict.__delitem__('mongodb_major_version')
        try:
            return_dict['replicationSpecs'] = [self.replication_specs[0].as_dict()]
        except AttributeError:
            return_dict['replicationSpecs'] = [self.replication_specs[0][0].as_dict()]
        return_dict.__delitem__('replication_specs')
        try:
            return_dict['stateName'] = self.state_name.name
            return_dict.__delitem__('state_name')
        except AttributeError:
            pass
        return_dict['providerSettings'] = self.providerSettings.as_dict()
        return_dict.__delitem__('replication_factor')  # THis has been deprecated, so removing from dict output
        return_dict['mongoDBVersion'] = self.mongodb_version
        return_dict.__delitem__('mongodb_version')
        return_dict['srvAddress'] = self.srv_address
        return_dict.__delitem__('srv_address')
        return_dict['mongoURI'] = self.mongo_uri
        return_dict.__delitem__('mongo_uri')
        return_dict['mongoURIWithOptions'] = self.mongod_uri_with_options
        return_dict.__delitem__('mongod_uri_with_options')
        return_dict['diskSizeGB'] = self.disk_size_gb
        return_dict.__delitem__('disk_size_gb')
        return_dict['pitEnabled'] = self.pit_enabled
        return_dict.__delitem__('pit_enabled')
        return_dict['numShards'] = self.num_shards
        return_dict.__delitem__('num_shards')
        return_dict['mongoURIUpdated'] = self.mongo_uri_updated
        return_dict.__delitem__('mongo_uri_updated')
        return_dict['backupEnabled'] = self.backup_enabled
        return_dict.__delitem__('backup_enabled')

        return return_dict


class AtlasBasicReplicaSet(object):
    def __init__(self, name: str,
                 size: InstanceSizeName = InstanceSizeName.M10,
                 disk_size: int = 10,
                 provider: ProviderName = ProviderName.AWS,
                 region: str = 'US_WEST_2',
                 version: MongoDBMajorVersion = MongoDBMajorVersion.v4_0,
                 ) -> None:
        provider_settings = ProviderSettings(size=size,
                                             provider=provider, region=region)
        regions_config = RegionConfig()
        replication_specs = ReplicationSpecs(regions_config={region: regions_config.__dict__})

        self.config: ClusterConfig = ClusterConfig(disk_size_gb=disk_size,
                                                   name=name,
                                                   mongodb_major_version=version,
                                                   providerSettings=provider_settings,
                                                   replication_specs=replication_specs)
        self.config_running = None
        self.config_pending = None
