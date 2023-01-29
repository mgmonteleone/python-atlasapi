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
Atlas module

Core module which provides access to MongoDB Atlas Cloud Provider APIs
"""
from atlasapi.network import Network
from atlasapi.errors import *
from pprint import pprint
from json import loads
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from atlasapi.specs import Host, ListOfHosts, DatabaseUsersUpdatePermissionsSpecs, ReplicaSetTypes
from atlasapi.measurements import AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement
from typing import List, Optional
from atlasapi.clusters import ClusterConfig, ShardedClusterConfig, AtlasBasicReplicaSet, \
    InstanceSizeName, AdvancedOptions, TLSProtocols, return_correct_cluster_config, ClusterView, OrgGroupView
from atlasapi.events import atlas_event_factory, EventsIterable
import logging
from typing import Union, Iterable, Set, BinaryIO, Iterator, Dict
from atlasapi.errors import ErrAtlasBadRequest
from atlasapi.alerts import Alert
from atlasapi.whitelist import WhitelistEntry
from atlasapi.maintenance_window import MaintenanceWindow
from atlasapi.lib import AtlasLogNames, LogLine, ProviderName, MongoDBMajorVersion, AtlasPeriods, AtlasGranularities
from atlasapi.cloud_backup import CloudBackupSnapshot, CloudBackupRequest, SnapshotRestore, SnapshotRestoreResponse, \
    DeliveryType
from atlasapi.projects import Project, ProjectSettings
from atlasapi.teams import TeamRoles
from atlasapi.atlas_users import AtlasUser
from atlasapi.organizations import Organization
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from atlasapi.events_event_types import AtlasEventTypes
from atlasapi.events import AtlasEvent
from atlasapi.invoices_pydantic import ApiInvoiceView
from atlasapi.serverless_pydantic import ServerlessInstance, ServerlessInstanceProviderSettings, BackingProviderName, \
    ServerlessProviderName, ServerlessRegionName, DeletedReturn
import gzip
import pytz

logger = logging.getLogger('Atlas')


# noinspection PyProtectedMember


class Atlas:
    """Atlas constructor

    Args:
        key (str): Atlas user
        secret (str): Atlas password
        group (str): Atlas group
        auth_method (Union[HTTPBasicAuth,HTTPDigestAuth]) : Authentication method to use, defaults to digest, but you
        can override to Basic if needed for use with a Proxy.
    """

    def __init__(self, key: str, secret: str, group: str = None,
                 auth_method: Union[HTTPBasicAuth, HTTPDigestAuth] = HTTPDigestAuth):
        self.group = group

        # Network calls which will handled user/password for auth
        self.network = Network(key, secret, auth_method)
        # APIs
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
        self.Clusters = Atlas._Clusters(self)
        self.Hosts = Atlas._Hosts(self)
        self.Events = Atlas._Events(self)
        self.logger = logging.getLogger(name='Atlas')
        self.Alerts = Atlas._Alerts(self)
        self.Whitelist = Atlas._Whitelist(self)
        self.MaintenanceWindows = Atlas._MaintenanceWindows(self)
        self.CloudBackups = Atlas._CloudBackups(self)
        self.Projects = Atlas._Projects(self)
        self.Organizations = Atlas._Organizations(self)
        self.Invoices = Atlas._Invoices(self)
        self.Serverless = Atlas._Serverless(self)
        if not self.group:
            self.logger.warning("Note! The Atlas client has been initialized without a Group/Project, some endpoints"
                                "will not function without a Group or project.")

    class _Clusters:
        """Clusters API

        see: https://docs.atlas.mongodb.com/reference/api/clusters/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def is_existing_cluster(self, cluster) -> bool:
            """Check if the cluster exists

            Not part of Atlas api but provided to simplify some code

            Args:
                cluster (str): The cluster name

            Returns:
                bool: The cluster exists or not
            """

            try:
                self.get_single_cluster(cluster)
                return True
            except ErrAtlasNotFound:
                return False

        def get_all_clusters(self) -> Iterable[ClusterConfig]:
            """Get All Clusters for a single Project.

            Yields ClusterConfig objects.

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-all/

            Returns:
                Iterable[ClusterConfig]: Iterable of ClusterConfigs (or ShardedClusterConfig)

            """

            uri = Settings.api_resources["Clusters"]["Get All Clusters"].format(GROUP_ID=self.atlas.group)
            response = self.atlas.network.get(Settings.BASE_URL + uri)
            for page in response:
                for each_cluster in page.get("results"):
                    yield return_correct_cluster_config(each_cluster)

        def get_all_authorized_clusters(self) -> Iterable[ClusterConfig]:
            """Get All Clusters which the current key is authorized

            Yields ClusterConfig objects.

            url: https://www.mongodb.com/docs/atlas/reference/api-resources-spec/#operation/returnAllAuthorizedClustersInAllProjects

            Returns:
                Iterable[ClusterConfig]: Iterable of ClusterConfigs (or ShardedClusterConfig)
                "groupId": "5fe75f61bc4b503859856896",
            "groupName": "AtlasApi",
            "orgId": "5ac52173d383ad0caf52e11c",
            "orgName": "MGM_Atlas",
            "planType": "Atlas",
            "tags": []

            """

            uri = Settings.api_resources["Clusters"]["Return All Authorized Clusters in All Projects"]
            response = self.atlas.network.get(Settings.BASE_URL + uri)
            for page in response:
                for each_group in page.get("results"):
                    groupId = each_group.get('groupId', None)
                    groupName = each_group.get('groupName', None)
                    orgId = each_group.get('orgId', None)
                    orgName = each_group.get('orgId', None)
                    planType = each_group.get('orgId', None)
                    tags = each_group.get('orgId', [])
                    cluster_list = []
                    for each_cluster in each_group.get('clusters', []):
                        cluster = ClusterView.parse_obj(each_cluster)
                        cluster_list.append(cluster)
                    group_data = OrgGroupView(clusters=cluster_list, group_id=groupId, group_name=groupName,
                                              org_id=orgId, org_name=orgName, plan_type=planType)

                    yield group_data

        def get_single_cluster(self, cluster: str) -> ClusterConfig:
            """Get a Single Cluster

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/

            Args:
                cluster (str): The cluster name

            Returns:
                ClusterConfig: A single ClusterConfig Object
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"].format(GROUP_ID=self.atlas.group,
                                                                                    CLUSTER_NAME=cluster)
            cluster_data = list(self.atlas.network.get(Settings.BASE_URL + uri))[0]

            return return_correct_cluster_config(cluster_data)

        def get_single_cluster_advanced_options(self, cluster: str) -> AdvancedOptions:
            """ Retrieves advanced options from a cluster.

            GET /groups/{groupId}/clusters/{clusterName}/processArgs

            :param cluster: the cluster name
            :return (AdvancedOptions): AdvancedOptions object
            """
            uri = Settings.api_resources["Clusters"]["Advanced Configuration Options"].format(GROUP_ID=self.atlas.group,
                                                                                              CLUSTER_NAME=cluster)
            advanced_options = self.atlas.network.get(Settings.BASE_URL + uri)

            advanced_data = list(advanced_options)[0]

            return AdvancedOptions(advanced_data)

        def get_single_cluster_as_obj(self, cluster) -> Union[ClusterConfig, ShardedClusterConfig]:
            """[DEPRECATED]Get a Single Cluster as data

            Legacy wrapper, now deprecated since we always return objects, never dicts.

            Args:
                cluster (str): The cluster name

            Returns:
                ClusterConfig (ClusterConfig): A cluster config
            """
            return self.get_single_cluster(cluster)

        def create_cluster(self, cluster: ClusterConfig) -> dict:
            """Create a cluster

            url: POST /api/atlas/v1.0/groups/{GROUP-ID}/clusters

            Args:
                cluster (ClusterConfig): A Cluster Config Object

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Clusters"]["Create a Cluster"].format(GROUP_ID=self.atlas.group)
            logger.info("Initiating Call to Atlas API at {}".format(Settings.BASE_URL + uri))
            logger.info("Cluster Config = {}".format(cluster))
            cluster_data = self.atlas.network.post(Settings.BASE_URL + uri, payload=cluster.as_create_dict())
            return cluster_data

        def create_basic_rs(self, name: str,
                            size: InstanceSizeName = InstanceSizeName.M10,
                            disk_size: int = 10,
                            provider: ProviderName = ProviderName.AWS,
                            region: str = 'US_WEST_2',
                            version: MongoDBMajorVersion = MongoDBMajorVersion.v4_0) -> AtlasBasicReplicaSet:
            """
            Simplified method for creating a basic replica set with basic options.

            :param name: The name for the cluster
            :param size: The Atlas Instance size, found in The InstanceSizeName enum
            :param disk_size: The size in GB for disk
            :param provider: The cloud provider, found in ProviderName enum
            :param region: The provider region to place the cluster.
            :param version: The mongodb major version (enum)
            :return: AtlasBasicReplicaSet
            """
            cluster: AtlasBasicReplicaSet = AtlasBasicReplicaSet(name=name, size=size, disk_size=disk_size,
                                                                 provider=provider, region=region,
                                                                 version=version)
            result = self.create_cluster(cluster=cluster.config)

            cluster.config_running = result
            return cluster

        def delete_cluster(self, cluster: str, areYouSure: bool = False):
            """Delete a Cluster

            url: https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/

            Args:
                cluster (str): Cluster name

            Keyword Args:
                areYouSure (bool): safe flag to don't delete a cluster by mistake

            Returns:
                dict: Response payload

            Raises:
                ErrConfirmationRequested: Need a confirmation to delete the cluster
                :type areYouSure: bool
                :param cluster: Cluster name
                :param areYouSure: safe flag to don't delete a cluster by mistake
            """
            if areYouSure:
                uri = Settings.api_resources["Clusters"]["Delete a Cluster"] % (self.atlas.group, cluster)
                return self.atlas.network.delete(Settings.BASE_URL + uri)
            else:
                raise ErrConfirmationRequested(
                    "Please set areYouSure=True on delete_cluster call if you really want to delete [%s]" % cluster)

        def modify_cluster(self, cluster: str, cluster_config: Union[ClusterConfig, dict]) -> dict:
            """Modify a Cluster

            Modifies an existing cluster in the project. Either from a full ClusterConfig object, or from a simple
            dict which contains the elements desired.


            url: https://docs.atlas.mongodb.com/reference/api/clusters-modify-one/


            :param cluster: The name of the cluster to modify
            :param cluster_config: A ClusterConfig object containing the new configuration,
                                   or a dict containing fragment.
            :return: dict:  A dictionary of the new cluster config
            """
            uri = Settings.api_resources["Clusters"]["Modify a Cluster"].format(GROUP_ID=self.atlas.group,
                                                                                CLUSTER_NAME=cluster)
            try:
                self.get_single_cluster_as_obj(cluster=cluster)
            except ErrAtlasNotFound:
                logger.error('Could not find existing cluster {}'.format(cluster))
                raise ValueError('Could not find existing cluster {}'.format(cluster))

            if type(cluster_config) in (ShardedClusterConfig, ClusterConfig):
                logger.debug("We received a full cluster_config, converting to dict")
                try:
                    new_config = cluster_config.as_modify_dict()
                except Exception as e:
                    logger.error('Error while trying to parse the new configuration')
                    raise e
            else:
                logger.debug("We received a simple dict for cluster config, sending without converting.")
                new_config = cluster_config
            value_returned = self.atlas.network.patch(uri=Settings.BASE_URL + uri, payload=new_config)
            return value_returned

        def modify_cluster_instance_size(self, cluster: str, new_cluster_size: InstanceSizeName) -> dict:
            """
            Modifies existing cluster by changing only the instance size.

            Helper function using modify_cluster
            :param cluster: The cluster name
            :param new_cluster_size: InstanceSizeName: The new size to use.
            :return: dict: the new cluster configuration dict

            """
            # Check new_cluster_size type:
            try:
                assert isinstance(new_cluster_size, InstanceSizeName)
            except AssertionError:
                raise TypeError(
                    f'new_cluster_size must be an instance of InstanceSizeName, not a {type(new_cluster_size)}')

            # First check to see if this is a new size, and if the cluster exists
            try:
                existing_config = self.get_single_cluster_as_obj(cluster=cluster)
                if existing_config.providerSettings.instance_size_name == new_cluster_size:
                    logger.error("New size is the same as old size.")
                    raise ValueError("New size is the same as old size.")
            except ErrAtlasNotFound:
                logger.error('Could not find existing cluster {}'.format(cluster))
                raise ValueError('Could not find existing cluster {}'.format(cluster))

            existing_config.providerSettings.instance_size_name = new_cluster_size
            return self.modify_cluster(cluster=cluster, cluster_config=existing_config)

        def modify_cluster_advanced_options(self, cluster: str,
                                            advanced_options: AdvancedOptions,
                                            ) -> AdvancedOptions:
            """
            Modifies cluster advanced options using a AdvancedOptions object.

            PATCH /groups/{GROUP-ID}/clusters/{CLUSTER-NAME}/processArgs

            :param cluster: The cluster name
            :param advanced_options: An AdvancedOptions object with the options to be set.
            :return:
            """
            uri = Settings.api_resources["Clusters"]["Advanced Configuration Options"].format(GROUP_ID=self.atlas.group,
                                                                                              CLUSTER_NAME=cluster)
            logger.info(f"The advanced options {advanced_options.as_dict}")
            value_returned = self.atlas.network.patch(uri=Settings.BASE_URL + uri, payload=advanced_options.as_dict)
            advanced_options_obj = AdvancedOptions.fill_from_dict(data_dict=value_returned)
            return advanced_options_obj

        def modify_cluster_tls(self, cluster: str, TLS_protocol: TLSProtocols) -> TLSProtocols:
            """Modifies cluster TLS settings.

            Helper class, just wraps modify_cluster_advanced_options.


            """
            advanced_options = AdvancedOptions(minimumEnabledTlsProtocol=TLS_protocol)

            return_val = self.modify_cluster_advanced_options(cluster=cluster, advanced_options=advanced_options)
            return return_val.minimumEnabledTlsProtocol

        def pause_cluster(self, cluster: str) -> bool:
            """
            Pauses/Unpauses a cluster.

            If you wish to unpause (resume) use the resume_cluster method.
            :rtype: dict
            :param cluster: The name of the cluster
            :return: bool: paused status
            """
            result = None
            existing_config = self.get_single_cluster(cluster=cluster)
            logger.info(f'The cluster state is currently Paused= {existing_config.paused}')
            if existing_config.paused is True:
                logger.warning("The cluster is already paused. Use unpause instead.")
                result = existing_config.paused
            elif existing_config.paused is False:
                logger.warning(f'Cluster is not paused, we will proceed with pausing')
                new_config = dict(paused=True)
                try:
                    self.modify_cluster(cluster=cluster, cluster_config=new_config)
                    result = True
                except ErrAtlasConflict as e:
                    logger.warning(f'We tried to pause the cluster, but it was recently resumed, so we are not '
                                   f'allowed to.')
                    raise e
            return result

        def resume_cluster(self, cluster: str) -> bool:
            """
            Pauses/Unpauses a cluster.

            :rtype: dict
            :param cluster: The name of the cluster
            :return: bool: The paused status
            """
            existing_config = self.get_single_cluster(cluster=cluster)
            logger.info(f'The cluster state is currently Paused= {existing_config.paused}')
            if existing_config.paused is True:
                logger.info("The cluster is paused. Will proceed with resuming")
                try:
                    new_config = dict(paused=False)
                    result = self.modify_cluster(cluster=cluster, cluster_config=new_config)
                    return result.get('paused')
                except ErrAtlasConflict:
                    logger.warning(f'We tried to resume the cluster, but it was resumed already in flight.')
                    return False
            elif existing_config.paused is False:
                logger.warning(f'The cluster {cluster} is already resumed, no need to resume')
                return False

        def test_failover(self, cluster: str) -> Optional[dict]:
            """
            Triggers a primary failover for a cluster

            Used for testing cluster resiliency.

            :rtype: dict
            :param cluster:
            :return: And empty dict
            """
            uri = Settings.api_resources["Clusters"]["Test Failover"].format(GROUP_ID=self.atlas.group,
                                                                             CLUSTER_NAME=cluster)

            return self.atlas.network.post(uri=Settings.BASE_URL + uri, payload={})

    class _Hosts:
        """Hosts API

        see: https://docs.atlas.mongodb.com/reference/api/monitoring-and-logs/#monitoring-and-logs

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas: atlas = atlas
            self.logger = logging.getLogger('Atlas.Hosts')
            self.host_list_with_measurements: Optional[List[Host]] = list()
            self.host_list: Optional[List[Host]] = list(self._get_all_hosts())

        def _get_all_hosts(self):
            """Get All Hosts (actually processes)

            Internal use only, actual data retrieval comes from properties host_list and host_names
            url: https://www.mongodb.com/docs/atlas/reference/api/processes-get-all/

            Keyword Args:


            Returns:
                ListOfHosts: Iterable object representing this function

            """
            uri = Settings.api_resources["Monitoring and Logs"]["Get all processes for group"].format(
                group_id=self.atlas.group)

            try:
                response = self.atlas.network.get(Settings.BASE_URL + uri)
                for page in response:
                    for each_process in page.get("results"):
                        yield Host(each_process)
            except Exception as e:
                raise e

        def fill_host_list(self, for_cluster: Optional[str] = None) -> Iterable[Host]:
            """
            Fills the `self.hostname` property with the current hosts for the project/group.

            Optionally, one can specify the `for_cluster` parameter to fill the host list with
            hosts only from the specified cluster.

            Args:
                for_cluster (str): The name of the cluster for filter the host list.

            Returns:
                Iterable[Host]: Yields `Host` objects
            """
            host_list = self._get_all_hosts()
            self.host_list = list()
            if for_cluster:
                out_list = list()
                for host in host_list:
                    if host.cluster_name.lower() == for_cluster.lower():
                        logger.info(f"Matching {host.cluster_name.lower()} to {for_cluster.lower()}")
                        logger.info(f"Host list is now {len(self.host_list)}")
                        self.host_list.append(host)
                    elif host.cluster_name_alias.lower() == for_cluster.lower():
                        logger.info(f"Matched {host.cluster_name_alias.lower()} to {for_cluster.lower()}")
                        logger.info(f"Host list is now {len(self.host_list)}")
                        self.host_list.append(host)
                logger.info(f"The host list is {len(self.host_list)} long")
            else:
                self.host_list = list(self._get_all_hosts())

            return self.host_list

        @property
        def host_names(self) -> Iterable[str]:
            """Returns a simple list of host names without port

            :rtype: Iterator[str]
            """

            for host in self.host_list:
                yield host.hostname

        @property
        def cluster_list(self) -> Set[str]:
            """
            Returns a list of clusters found in the hosts for this group.

            Returns:
                Set[str}: A set of cluster names
            """
            cluster_list = set()
            for host in self.host_list:
                cluster_list.add(host.cluster_name)
            return cluster_list

        def host_list_by_cluster(self, cluster_name: str) -> Iterable[Host]:
            """
            Returns hosts belonging to the named cluster.
            Args:
                cluster_name (str):
            Returns:
                 Iterable[Host]: An interator of Host Objects.
            """
            for host in self.host_list:
                if host.cluster_name.lower() == cluster_name.lower():
                    logger.info(f"Matching {host.cluster_name.lower()} to {cluster_name.lower()}")
                    logger.info(f"Host list is now {len(self.host_list)}")
                    yield host
                elif host.cluster_name_alias.lower() == cluster_name.lower():
                    logger.info(f"Matched {host.cluster_name_alias.lower()} to {cluster_name.lower()}")
                    logger.info(f"Host list is now {len(self.host_list)}")
                    yield host


        def update_host_list(self, host_obj: Host) -> None:
            """
            Places a host into the host_list property.

            Args:
                host_obj: Host: A host object with measurements.

            Returns:
                None:
            """
            for n, i in enumerate(self.host_list):
                if i == host_obj:
                    self.host_list[n] = host_obj
            self.logger.info("Added new host item")

        @property
        def host_list_primaries(self) -> Iterable[Host]:
            """Yields only hosts which are currently primary.

            """
            for each_host in self.host_list:
                if each_host.type == ReplicaSetTypes.REPLICA_PRIMARY:
                    yield each_host

        @property
        def host_list_secondaries(self) -> Iterable[Host]:
            """Yields only hosts which are currently secondaries.

            """
            for each_host in self.host_list:
                if each_host.type == ReplicaSetTypes.REPLICA_SECONDARY:
                    yield each_host

        def get_measurement_for_hosts(self, granularity: Optional[AtlasGranularities] = None,
                                      period: Optional[AtlasPeriods] = None,
                                      measurement: Optional[AtlasMeasurementTypes] = None, return_data: bool = False):
            """Get measurement(s) for all hosts in the host_list


                        Populates all hosts in the host_list with the requested metric.

                        Multiple calls will append additional metrics to the same host object.

                        Please note that using the `return_data`  param will also return the updated
                        host objects, which may unnecessarily consume memory.

                        Keyword Args:
                            granularity (AtlasGranularities): the desired granularity
                            period (AtlasPeriods): The desired period
                            measurement (AtlasMeasurementTypes) : The desired measurement or Measurement class



                            :param return_data:
                            :rtype: List[measurements.AtlasMeasurement]
                            :type period: AtlasPeriods
                            :type granularity: AtlasGranularities
                            :type measurement: measurements.AtlasMeasurementTypes
                        """

            if not self.host_list:
                raise (ValueError('Before retrieving measurements for hosts, you must retrieve the host list'
                                  ' by using one of the `fill_host_list`.'))
            return_list = list()
            for each_host in self.host_list:
                logger.info('Pulling measurements for {} hosts'.format(len(self.host_list)))
                logger.info(f'Measurement: {measurement}')
                logger.info('Metric: {}'.format(granularity.__str__()))
                logger.info('For Period: {}'.format(period.__str__()))
                try:
                    logger.debug(f'The data type of measurement is is {type(measurement)}')
                    returned_data = self._get_measurement_for_host(each_host, granularity=granularity,
                                                                   period=period,
                                                                   measurement=measurement)
                    each_host.measurements = list(returned_data)
                except Exception as e:
                    logger.error('An error occurred while retrieving metrics for host: {}.'
                                 'The error was {}'.format(each_host.hostname, e))
                    logger.warning('Will continue with next host. . . ')
                return_list.append(each_host)
            self.host_list_with_measurements = return_list
            if return_data:
                return return_list

        def get_log_for_host(self, host_obj: Host,
                             log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                             date_from: datetime = None,
                             date_to: datetime = None,
                             ) -> BinaryIO:
            """
            Retrieves the designated logfile archive of designated log_name and for the designated dates,
            and returns a binary file like object.

            Args:
                host_obj (Host): And atlas Host object to retrieve logs for
                log_name (AtlasLogNames): an AtlasLogNames type
                date_from (datetime.datetime): The datetime to start from
                date_to (datetime.datetime): The datetime to gather till

            Returns:
                BinaryIO: A BinaryIO object containing the gzipped log file.

            """
            uri = Settings.api_resources["Monitoring and Logs"]["Get the log file for a host in the cluster"].format(
                group_id=self.atlas.group,
                host=host_obj.hostname,
                logname=log_name.value,
                date_from=date_from,
                date_to=date_to
            )
            params = dict()
            if date_from:
                try:
                    date_from = pytz.utc.localize(date_from)
                except ValueError:
                    logger.info(f'The date_from value {date_from} is already localized. Will not re-localize.')
                    pass

                params.update({'startDate': int(round(date_from.timestamp()))})
            if date_to:
                try:
                    date_to = pytz.utc.localize(date_to)
                except ValueError:
                    logger.info(f'The date_to value {date_to} is already localized. Will not re-localize.')
                    pass
                params.update({'endDate': int(round(date_to.timestamp()))})

            # Build the request
            logger.info(f'The URI used will be {uri}')
            return_val = self.atlas.network.get_file(Settings.BASE_URL + uri, params=params)
            return return_val

        def get_loglines_for_host(self, host_obj: Host,
                                  log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                                  date_from: datetime = None,
                                  date_to: datetime = None,
                                  ) -> Iterable[LogLine]:
            """
            Gathers the designated log file from Atlas, and then returns the lines therein contained.

            Does so by downloading the gzip file into memory, ungzipping and then unpacking each log line
            as a LogLine Object.

            Args:
                host_obj (Host): An atlas Host object to retrive logs for
                log_name (str): an AtlasLogNames type
                date_from (datetime): The datetime to start from
                date_to (datetime): The datetime to gather till

            Returns:
                Iterable[LogLine] : Yeilds LogLine objects, one for each logline found in the file.
            """
            result = self.get_log_for_host(host_obj, log_name, date_from, date_to)
            result.seek(0)
            content = gzip.GzipFile(fileobj=result)
            for each in content.readlines():
                yield LogLine(each.decode())

        def get_logs_for_project(self,
                                 log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                                 date_from: datetime = None,
                                 date_to: datetime = None) -> Iterable[Host]:
            """
            Yields A Host object per Host in the project with  a File-like objects containing the gzipped log file
            requested for each  host in the project using the same date filters and log_name (type) in the log_files
            property.

            Currently the log_file property (List) is usually with only one item.
            Args:
                log_name (AtlasLogNames): The type of log to be retrieved
                date_from (datetime) : Start of log entries
                date_to (datetime): End of log entries

            Returns:
                Iterable[Host]: Yields Host objects, with full host information as well as the logfile in the log_files
                property.
            """
            for each_host in self.host_list:
                try:
                    log_file: BinaryIO = self.get_log_for_host(host_obj=each_host,
                                                               log_name=log_name,
                                                               date_from=date_from,
                                                               date_to=date_to)
                except Exception as e:
                    raise e
                each_host.add_log_file(name=log_name, file=log_file)
                yield each_host

        def get_logs_for_cluster(self,
                                 cluster_name: str,
                                 log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                                 date_from: datetime = None,
                                 date_to: datetime = None) -> Iterable[Host]:
            """
            Yields A Host object per Host in the passed cluster with  a File-like objects containing the gzipped
            log file requested for each  host in the project using the same date filters and log_name (type) in the
            log_files property.

            Currently the log_file property (List) is usually with only one item.
            Args:
                cluster_name (str) :
                log_name (AtlasLogNames): The type of log to be retrieved
                date_from (datetime) : Start of log entries
                date_to (datetime): End of log entries

            Returns:
                Iterable[Host]: Yields Host objects, with full host information as well as the logfile in the log_files
                property.
            """
            self.fill_host_list(for_cluster=cluster_name)
            for each_host in self.host_list:
                try:
                    logger.warning(f"Now retrieving log file for {each_host}, this may take a while....")
                    log_file: BinaryIO = self.get_log_for_host(host_obj=each_host,
                                                               log_name=log_name,
                                                               date_from=date_from,
                                                               date_to=date_to)
                except Exception as e:
                    raise e
                each_host.add_log_file(name=log_name, file=log_file)
                yield each_host

        def _get_measurement_for_host(self, host_obj: Host,
                                      granularity: Optional[AtlasGranularities] = None,
                                      period: Optional[AtlasPeriods] = None,
                                      measurement: Optional[AtlasMeasurementTypes] = None
                                      ) -> Iterable[AtlasMeasurement]:
            """Get  measurement(s) for a host

            Internal use only, should come from the host obj itself.

            Returns measurements for the passed Host object.

            url: https://docs.atlas.mongodb.com/reference/api/process-measurements/


            Accepts either a single measurement, but will retrieve more than one measurement
            if the measurement (using the AtlasMeasurementTypes class)

            /api/atlas/v1.0/groups/{GROUP-ID}/processes/{HOST}:{PORT}/measurements

            Keyword Args:
                host_obj (Host): the host
                granularity (AtlasGranuarities): the desired granularity
                period (AtlasPeriods): The desired period
                measurement (AtlasMeasurementTypes) : The desired measurement or Measurement class
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                 Iterable[AtlasMeasurement] or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits

                :rtype: List[measurements.AtlasMeasurement]
                :type period: AtlasPeriods
                :type granularity: AtlasGranularities
                :type host_obj: Host
                :type measurement: measurements.AtlasMeasurementTypes

            """

            #  Set default measurement, period and granularity if none are sent
            if measurement is None:
                measurement = AtlasMeasurementTypes.Cache.dirty
            if period is None:
                period = AtlasPeriods.WEEKS_1
            if granularity is None:
                granularity = AtlasGranularities.HOUR

            # Check to see if we received a leaf or branch of the measurements
            logger.debug(f'Measurement is: {measurement}')
            logger.debug(f'Measurement object type is {type(measurement)}')
            try:
                parent = super(measurement)
                self.logger.error('We received a branch, whos parent is {}'.format(parent.__str__()))
                leaves = measurement.get_all()
                measurement_list = list(leaves)
                measurement = '&m='.join(measurement_list)
            except TypeError:
                self.logger.info('We received a leaf')

            # Build the URL

            if isinstance(measurement, tuple):
                logger.debug(f'Somehow got a tuple for measurement {measurement}. Need to get the str')
                measurement: tuple = measurement[0]
            if isinstance(granularity, tuple):
                logger.info(f'Somehow got a tuple for granularity {granularity}. Need to get the str')
                granularity: tuple = granularity[0]
            if isinstance(period, tuple):
                logger.debug(f'Somehow got a tuple for period {period}. Need to get the str')
                period: tuple = period[0]

            uri = Settings.api_resources["Monitoring and Logs"]["Get measurement for host"].format(
                group_id=self.atlas.group,
                host=host_obj.hostname,
                port=host_obj.port,
                granularity=granularity,
                period=period,
                measurement=measurement
            )
            logger.debug(f'The URI used will be {uri}')
            # Build the request
            return_val = self.atlas.network.get(Settings.BASE_URL + uri)
            for each_host in return_val:
                try:
                    measurements = each_host.get('measurements')
                except Exception as e:
                    logger.error(f"Error getting measurements from results")

                    logger.error(e)
                    logger.error(f"The results look like {results}")
                    logger.error(f"The results have length {len(list(results))}")
                    for each in results:
                        logger.error(f"Results are: {each}")
                    raise e
                measurements_count = len(measurements)
                self.logger.info('There are {} measurements.'.format(measurements_count))

                for each in measurements:
                    measurement_obj = AtlasMeasurement(name=each.get('name'),
                                                       period=period,
                                                       granularity=granularity)
                    for each_and_every in each.get('dataPoints'):
                        measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

                yield measurement_obj

    class _Events:
        """Events API

        see: https://docs.atlas.mongodb.com/reference/api/events/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas  # type: Atlas
            self.logger = logging.getLogger('Atlas.Events')  # type: logging

        def _get_all_project_events(self, since_datetime: datetime = None):
            """Get All Project Events

            Internal use only, actual data retrieval comes from properties all
            url: https://docs.atlas.mongodb.com/reference/api/events-projects-get-all/

            Keyword Args:
                since_datetime (datetime): Date and time from when Atlas starts returning events.

            Yields:
                AtlasEvent: An Atlas Event
            """
            if since_datetime:
                uri = Settings.api_resources["Events"]["Get Project Events Since Date"].format(
                    min_date=since_datetime.isoformat(),
                    group_id=self.atlas.group)
            else:
                uri = Settings.api_resources["Events"]["Get All Project Events"].format(
                    group_id=self.atlas.group)
            response = self.atlas.network.get(Settings.BASE_URL + uri)
            for page in response:
                for event in page["results"]:
                    yield atlas_event_factory(event)

        def _get_project_events_by_type(self, event_type: AtlasEventTypes, since_datetime: datetime = None,
                                        pageNum: int = Settings.pageNum,
                                        itemsPerPage: int = Settings.itemsPerPage,
                                        iterable: bool = False) -> Union[List[dict], Iterable[AtlasEvent]]:
            """Get All Project Events For A Single type

            Internal use only, actual data retrieval comes from properties all
            url: https://docs.atlas.mongodb.com/reference/api/events-projects-get-all/

            Keyword Args:
                event_type (AtlasEventType):
                since_datetime (datetime):
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                ListOfEvents or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
                :rtype: Union[ListOfEvents, dict]
                :type iterable: OptionalBool
                :type itemsPerPage: OptionalInt
                :type pageNum: OptionalInt

            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                item_list = list(EventsGetForProjectAndType(self.atlas, event_type, since_datetime,
                                                            pageNum, itemsPerPage))
                obj_list: ListOfEvents = list()
                for item in item_list:
                    obj_list.append(atlas_event_factory(item))
                return obj_list

            if since_datetime:
                uri = Settings.api_resources["Events"]["Get Project Events Since Date"].format(
                    min_date=since_datetime.isoformat(),
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage) + f'&eventType={event_type.name}'

                return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            else:
                uri = Settings.api_resources["Events"]["Get All Project Events"].format(
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage) + f'&eventType={event_type.name}'
                return_val = self.atlas.network.get(Settings.BASE_URL + uri)
            return return_val

        @property
        def all(self) -> EventsIterable:
            """
            Returns an iterable of all events for the current project/group.

            Yields:
                EventsIterable: An iterable of event objects.

            """
            yield from self._get_all_project_events()

        def since(self, since_datetime: datetime) -> EventsIterable:
            """
            Returns an iterable of all events since the passed datetime. (UTC)

            Yields:
                EventsIterable: An iterable of event objects.
            """
            yield from self._get_all_project_events(since_datetime=since_datetime)

        def since_by_type(self, since_datetime: datetime, event_type: AtlasEventTypes):
            """Returns all events since the passed detetime (UTC) for the passed AtlasEvent Type

            Args:
                since_datetime (datetime):
                event_type (AtlasEventTypes):

            Returns:

            """
            return self._get_project_events_by_type(event_type=event_type, since_datetime=since_datetime, iterable=True)

    class _DatabaseUsers:
        """Database Users API

        see: https://docs.atlas.mongodb.com/reference/api/database-users/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas) -> None:
            self.atlas = atlas

        def get_all_database_users(self, pageNum: int = Settings.pageNum, itemsPerPage: int = Settings.itemsPerPage,
                                   iterable: bool = False):
            """Get All Database Users

            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-all-users/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return DatabaseUsersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Database Users"]["Get All Database Users"] % (
                self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_a_single_database_user(self, user: str) -> dict:
            """Get a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-get-single-user/

            Args:
                user (str): User

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Get a Single Database User"] % (self.atlas.group, user)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def create_a_database_user(self, permissions) -> dict:
            """Create a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-create-a-user/

            Args:
                permissions (DatabaseUsersPermissionsSpec): Permissions to apply

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Create a Database User"] % self.atlas.group
            return self.atlas.network.post(Settings.BASE_URL + uri, permissions.getSpecs())

        def update_a_database_user(self, user: str, permissions: DatabaseUsersUpdatePermissionsSpecs) -> dict:
            """Update a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-update-a-user/

            Args:
                user (str): User
                permissions (DatabaseUsersUpdatePermissionsSpecs): Permissions to apply

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Update a Database User"] % (self.atlas.group, user)
            logger.info(Settings.BASE_URL + uri, permissions.getSpecs())
            return self.atlas.network.patch(Settings.BASE_URL + uri, permissions.getSpecs())

        def delete_a_database_user(self, user: str) -> dict:
            """Delete a Database User

            url: https://docs.atlas.mongodb.com/reference/api/database-users-delete-a-user/

            Args:
                user (str): User to delete

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Database Users"]["Delete a Database User"] % (self.atlas.group, user)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

    class _Alerts:
        """Alerts API

        see: https://docs.atlas.mongodb.com/reference/api/alerts/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_alerts(self, status=None, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage,
                           iterable=False):
            """Get All Alerts

            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/

            Keyword Args:
                status (AlertStatusSpec): filter on alerts status
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return AlertsGetAll(self.atlas, status, pageNum, itemsPerPage)

            if status:
                uri = Settings.api_resources["Alerts"]["Get All Alerts with status"] % (
                    self.atlas.group, status, pageNum, itemsPerPage)
            else:
                uri = Settings.api_resources["Alerts"]["Get All Alerts"] % (self.atlas.group, pageNum, itemsPerPage)

            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_an_alert(self, alert: str) -> Alert:
            """Get an Alert

            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-alert/

            Args:
                alert (str): The alert id

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Alerts"]["Get an Alert"] % (self.atlas.group, alert)
            result = self.atlas.network.get(Settings.BASE_URL + uri)
            return Alert(result)

        # TODO: FIX THIS
        def acknowledge_an_alert(self, alert, until, comment=None):
            """Acknowledge an Alert

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id
                until (datetime): Acknowledge until

            Keyword Args:
                comment (str): The acknowledge comment

            Returns:
                dict: Response payload
                :param comment:
            """

            # data = {"acknowledgedUntil": until.isoformat(timespec='seconds')}
            data = {"acknowledgedUntil": "2017-10-23T08:28:35Z"}
            if comment:
                data["acknowledgementComment"] = comment

            uri = Settings.api_resources["Alerts"]["Acknowledge an Alert"] % (self.atlas.group, alert)
            return self.atlas.network.patch(Settings.BASE_URL + uri, data)

        # TODO: FIX THIS
        def unacknowledge_an_alert(self, alert):
            """Acknowledge an Alert

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id

            Returns:
                dict: Response payload
            """

            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To unacknowledge a previously acknowledged alert, set the field value to the past.
            now = datetime.now(timezone.utc)
            until = now - relativedelta(days=1)
            return self.acknowledge_an_alert(alert, until)

        # TODO: FIX THIS
        def acknowledge_an_alert_forever(self, alert, comment=None):
            """Acknowledge an Alert forever

            url: https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/

            Args:
                alert (str): The alert id

            Keyword Args:
                comment (str): The acknowledge comment

            Returns:
                dict: Response payload
            """

            # see https://docs.atlas.mongodb.com/reference/api/alerts-acknowledge-alert/#request-body-parameters
            # To acknowledge an alert “forever”, set the field value to 100 years in the future.
            now = datetime.now(timezone.utc)
            until = now + relativedelta(years=100)
            return self.acknowledge_an_alert(alert, until, comment)

    class _Whitelist:
        """Whitelist API

        see: https://docs.atlas.mongodb.com/reference/api/whitelist/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_all_whitelist_entries(self, pageNum: int = Settings.pageNum, itemsPerPage: int = Settings.itemsPerPage,
                                      iterable: bool = False) -> Iterable[WhitelistEntry]:
            """Get All whitelist entries

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-get-all/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                AtlasPagination or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                return WhitelistGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Whitelist"]["Get All Whitelist Entries"] % (
                self.atlas.group, pageNum, itemsPerPage)

            response = self.atlas.network.get(Settings.BASE_URL + uri)

            for entry in response.get('results', []):
                yield WhitelistEntry.fill_from_dict(entry)

        def get_whitelist_entry(self, ip_address: str) -> WhitelistEntry:
            """Get a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-get-one-entry/

            Args:
                ip_address (str): ip address to fetch from whitelist

            Returns:
                WhitelistEntry: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Get Whitelist Entry"] % (
                self.atlas.group, ip_address)
            response: dict = self.atlas.network.get(Settings.BASE_URL + uri)
            return WhitelistEntry.fill_from_dict(response)

        def create_whitelist_entry(self, ip_address: str, comment: str) -> List[WhitelistEntry]:
            """Create a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-add-one/

            Args:
                ip_address (str): ip address to add to whitelist
                comment (str): comment describing the whitelist entry

            Returns:
                List[WhitelistEntry]: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Create Whitelist Entry"] % self.atlas.group

            whitelist_entry = {'ipAddress': ip_address, 'comment': comment}
            response = self.atlas.network.post(Settings.BASE_URL + uri, [whitelist_entry])
            for entry in response.get('results', []):
                yield WhitelistEntry.fill_from_dict(entry)

        def delete_a_whitelist_entry(self, ip_address: str) -> dict:
            """Delete a whitelist entry

            url: https://docs.atlas.mongodb.com/reference/api/whitelist-delete-one/

            Args:
                ip_address (str): ip address to delete from whitelist

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Whitelist"]["Delete Whitelist Entry"] % (
                self.atlas.group, ip_address)
            return self.atlas.network.delete(Settings.BASE_URL + uri)

    class _MaintenanceWindows:
        """Maintenance Windows API

        see: https://docs.atlas.mongodb.com/reference/api/maintenance-windows/

        The maintenanceWindow resource provides access to retrieve or update the current Atlas project maintenance
         window. To learn more about Maintenance Windows, see the Set Preferred Cluster Maintenance Start Time setting
         on the View/Modify Project Settings page.

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def _get_maint_window(self, as_obj: bool = True) -> Union[dict, MaintenanceWindow]:
            """
            (Internal)Gets the current maint window configuration for the project.

            the current_config should be used instead.

            Args:
                as_obj: Return data as a MaintenanceWindowObj

            Returns:

            """
            uri = Settings.api_resources["Maintenance Windows"]["Get Maintenance Window"].format(
                GROUP_ID=self.atlas.group)
            response = self.atlas.network.get(Settings.BASE_URL + uri)
            if as_obj is False:
                logger.error("V3 always returns objects")
                raise DeprecationWarning("V3 Always returns objects, the as_obj=False setting is deprecated.")
            response_obj = list(response)[0]
            return MaintenanceWindow.from_dict(response_obj)

        def _update_maint_window(self, new_config: MaintenanceWindow) -> bool:
            """
            Uses the patch endpoint to update maint window settings.

            Args:
                as_obj: Return data as a MaintenanceWindowObj

            Returns:

            """

            uri = Settings.api_resources["Maintenance Windows"]["Update Maintenance Window"].format(
                GROUP_ID=self.atlas.group)
            self.atlas.network.patch(Settings.BASE_URL + uri, payload=new_config.as_update_dict())

            return True

        def _defer_maint_window(self) -> bool:
            """
            Used to defer the current maint window.

            TODO: Is this private method really needed? It is orignally here to provide a more flexible method to use
            if the public one was too simple, but may not be needed in the end.
            Returns:

            """
            uri = Settings.api_resources["Maintenance Windows"]["Defer Maintenance Window"].format(
                GROUP_ID=self.atlas.group)
            try:
                self.atlas.network.post(uri=Settings.BASE_URL + uri, payload={})
            except ErrAtlasBadRequest as e:
                if e.details.get('errorCode', None) == 'ATLAS_MAINTENANCE_NOT_SCHEDULED':
                    logger.warning(e.details.get('detail', 'No Detail available'))
                    return False
                else:
                    raise e
            return True

        def defer(self) -> dict:
            """
            Defers the currently scheduled maintenance window.

            Returns: bool:

            """
            output = self._defer_maint_window()
            return dict(maint_deffered=output)

        def current_config(self) -> MaintenanceWindow:
            """
            The current Maintainable Window configuration.

            Returns: MaintainableWindow object

            """
            return self._get_maint_window(as_obj=True)

        def set_config(self, new_config: MaintenanceWindow) -> bool:
            """
            Sets the maint configuration to the values in the passed MaintWindow Object

            Will only set those values which are not none in the MaintWindow Object. Currently, you can not use
            this method to set a value as null. (This is not supported by the API anyway)

            Args:
                new_config: A MaintainenceWindow Object

            Returns: bool: True is success

            """
            output: bool = self._update_maint_window(new_config=new_config)
            return output

    class _CloudBackups:
        """Cloud Backup  API

        see: https://docs.atlas.mongodb.com/reference/api/cloud-backup/backup/backups/

        The CloudBackups resource provides access to retrieve the Cloud provider backup snapshots.

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def create_snapshot_for_cluster(self, cluster_name: str, retention_days: int = 7,
                                        description: str = None) -> CloudBackupSnapshot:
            """
            Creates and on demand snapshot for the passed cluster

            Args:
                cluster_name:
                retention_days:
                description:
            """
            request_obj = CloudBackupRequest(cluster_name=cluster_name,
                                             retention_days=retention_days,
                                             description=description)

            uri = Settings.api_resources["Cloud Backup"]["Take an on-demand snapshot"] \
                .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name)

            try:
                response = self.atlas.network.post(uri=Settings.BASE_URL + uri, payload=request_obj.as_dict)
            except ErrAtlasBadRequest:
                logger.warning('Received an Atlas bad request on Snapshot creation. Could be due to overlap')
                raise IOError("Got a bad request error back from Atlas, this may be due to submitting"
                              "a snapshot request before a previous request has "
                              "completed.")
            logger.warning(f'Create response: {response}')
            return CloudBackupSnapshot(response)

        def get_backup_snapshots_for_cluster(self, cluster_name: str) -> Iterable[CloudBackupSnapshot]:
            """Get  backup snapshots for a cluster.


            Retrieves
            url: https://docs.atlas.mongodb.com/reference/api/cloud-backup/backup/backups/

            Keyword Args:
                cluster_name (str) : The cluster name to fetch

            Returns:
                AtlasPagination : Iterable object representing this function
            """

            uri = Settings.api_resources["Cloud Backup"]["Get all Cloud Backups for cluster"] \
                .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name)

            logger.debug(f"The cloudbackup uri used is {Settings.BASE_URL}{uri}")

            response = self.atlas.network.get(Settings.BASE_URL + uri)
            try:
                for each_page in response:
                    for each_bu in each_page.get("results"):
                        yield CloudBackupSnapshot.from_dict(each_bu)
            except KeyError as e:
                raise e

        def get_backup_snapshot_for_cluster(self, cluster_name: str, snapshot_id: str) -> CloudBackupSnapshot:
            """Get  singe backup snapshot for a cluster.

            Retrieves
            url: https://docs.atlas.mongodb.com/reference/api/cloud-backup/backup/backups/

            Keyword Args:
                cluster_name (str) : The cluster name to fetch

            Returns:
                Iterable[CloudBackupSnapshot]: Iterable object representing this function.

            """
            logger.info('Getting by snapshotid')
            uri = Settings.api_resources["Cloud Backup"]["Get snapshot by SNAPSHOT-ID"] \
                .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name, SNAPSHOT_ID=snapshot_id)

            logger.debug(f"The cloudbackup uri used is {Settings.BASE_URL}{uri}")

            response = self.atlas.network.get(Settings.BASE_URL + uri)
            try:
                return_list = list()
                for each_page in response:
                    return_list.append(CloudBackupSnapshot.from_dict(each_page))
                return return_list[0]
            except KeyError as e:
                raise e

        def is_existing_snapshot(self, cluster_name: str, snapshot_id: str) -> bool:
            """Returns true if the snaphost_id exists for the cluster

            Args:
                cluster_name:
                snapshot_id:

            Returns (bool):

            """
            try:
                out = self.atlas.CloudBackups.get_backup_snapshot_for_cluster(cluster_name, snapshot_id)
                if out:
                    return True
                else:
                    return False
            except (ErrAtlasNotFound, ErrAtlasBadRequest):
                return False

        def request_snapshot_restore(self, source_cluster_name: str, snapshot_id: str,
                                     target_cluster_name: str,
                                     delivery_type: DeliveryType = DeliveryType.automated,
                                     allow_same: bool = False
                                     ) -> SnapshotRestoreResponse:
            # Check if the target_cluster_name is valid
            if not self.atlas.Clusters.is_existing_cluster(target_cluster_name):
                logger.error(f'The passed target cluster {target_cluster_name}, does not exist in this project.')
                raise ValueError(f'The passed target cluster {target_cluster_name}, does not exist in this project.')
            else:
                logger.info('The target cluster exists.')
            # Check if the snapshot_id is valid
            if not self.atlas.CloudBackups.is_existing_snapshot(source_cluster_name, snapshot_id):
                error_text = f'The passed snapshot_id ({snapshot_id} ' \
                             f'is not valid for the source cluster {source_cluster_name})'
                logger.error(error_text)
                raise ValueError(error_text)
            else:
                logger.info('The snapshot_id is valid')

            # Check if the source and target clusters are the same, if so raise exception unless override is True

            if source_cluster_name == target_cluster_name and not allow_same:
                error_text = f'The source and target cluster should not be the same, as this is usually not the ' \
                             f'intended use case, and can lead to production data loss. If you wish to restore a ' \
                             f' snapshot to the same cluster, use the `allow_same` = True parameter.'
                logger.error(error_text)
                raise ValueError(error_text)

            uri = Settings.api_resources["Cloud Backup Restore Jobs"]["Restore snapshot by cluster"] \
                .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=source_cluster_name)

            request_obj = SnapshotRestore(delivery_type, snapshot_id, target_cluster_name, self.atlas.group)

            try:
                response = self.atlas.network.post(uri=Settings.BASE_URL + uri, payload=request_obj.as_dict)
            except ErrAtlasBadRequest as e:
                if e.details.get('errorCode') == 'CLUSTER_RESTORE_IN_PROGRESS_CANNOT_UPDATE':
                    logger.error(e.details)
                    raise ErrAtlasRestoreConflictError(c=400, details=e.details)
                else:
                    logger.error('Received an Atlas bad request on Snapshot restore request.')
                    logger.error(e.details)
                    raise IOError("Received an Atlas bad request on Snapshot restore request.")

            try:
                response_obj = SnapshotRestoreResponse.from_dict(response)
            except KeyError as e:
                logger.error('Error encountered parsing response to a SnapshotRestoreResponse')
                logger.error(e)
                raise e
            return response_obj

        def request_snapshot_restore_to_group(self, source_cluster_name: str, snapshot_id: str,
                                              target_cluster_name: str,
                                              target_group_obj,
                                              delivery_type: DeliveryType = DeliveryType.automated

                                              ) -> SnapshotRestoreResponse:
            """Requests a snapshot restore to another group/project.

            Uses the passed target_group_obj, which is an Atlas object, to restore a snapshot from one group/project
            to another.

            This method does not check if the source and destination clusters have the same name, since this would
            not be dangerous when these are in two groups.

            Args:
                source_cluster_name: the text name of the source cluster
                snapshot_id: the uuid id of the snapshot to be restored
                target_cluster_name: the txt name of the destination cluster
                target_group_obj: Atlas: An Atlas object connected to the destination group.
                delivery_type: DeliveryType: IF you want to download, or automatically restore on Atlas.

            Returns:

            """
            # Check if the source and target groups are actually the same....
            if target_group_obj.group == self.atlas.group:
                txt = f"The source and target groups are the same ({self.atlas.group}). this method should only " \
                      f"be used if the restore is to anothe group than the target."
                logger.error(txt)
                raise AttributeError(txt)

            # Check if the target_cluster_name is valid
            if not target_group_obj.Clusters.is_existing_cluster(target_cluster_name):
                logger.error(f'The passed target cluster {target_cluster_name}, does not exist in this project.)')
                raise ValueError(f'The passed target cluster {target_cluster_name}, does not exist in this project.')
            else:
                logger.info('The target cluster exists in the other target group.')
            # Check if the snapshot_id is valid
            if not self.atlas.CloudBackups.is_existing_snapshot(source_cluster_name, snapshot_id):
                error_text = f'The passed snapshot_id ({snapshot_id} ' \
                             f'is not valid for the source cluster {source_cluster_name})'
                logger.error(error_text)
                raise ValueError(error_text)
            else:
                logger.info('The snapshot_id is valid')

            uri = Settings.api_resources["Cloud Backup Restore Jobs"]["Restore snapshot by cluster"] \
                .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=source_cluster_name)

            request_obj = SnapshotRestore(delivery_type, snapshot_id, target_cluster_name, target_group_obj.group)

            try:
                response = self.atlas.network.post(uri=Settings.BASE_URL + uri, payload=request_obj.as_dict)
            except ErrAtlasBadRequest as e:
                if e.details.get('errorCode') == 'CLUSTER_RESTORE_IN_PROGRESS_CANNOT_UPDATE':
                    logger.error(e.details)
                    raise ErrAtlasRestoreConflictError(c=400, details=e.details)
                else:
                    logger.error('Received an Atlas bad request on Snapshot restore request.')
                    logger.error(e.details)
                    raise IOError("Received an Atlas bad request on Snapshot restore request.")

            try:
                response_obj = SnapshotRestoreResponse.from_dict(response)
            except KeyError as e:
                logger.error('Error encountered parsing response to a SnapshotRestoreResponse')
                logger.error(e)
                raise e
            return response_obj

        # Get all Cloud Backup restore jobs by cluster
        def get_snapshot_restore_requests(self, cluster_name: str, restore_id: str = None) \
                -> Iterator[SnapshotRestoreResponse]:

            if not restore_id:
                logger.warning("No restore_id passed, will return all restore jobs for this cluster.")
                uri = Settings.api_resources["Cloud Backup Restore Jobs"][
                    "Get all Cloud Backup restore jobs by cluster"] \
                    .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name)
            else:
                logger.warning('Getting by restore_id')
                uri = Settings.api_resources["Cloud Backup Restore Jobs"]["Get Cloud Backup restore job by cluster"] \
                    .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name, JOB_ID=restore_id)

            logger.info(f"The restore job uri used is {Settings.BASE_URL}{uri}")

            response = self.atlas.network.get(Settings.BASE_URL + uri)

            try:
                for each_page in response:
                    try:
                        for each_restore in each_page.get("results"):
                            yield SnapshotRestoreResponse.from_dict(each_restore)
                    except TypeError:
                        logger.warning("There was no results property, so should have gotten a single result")
                        yield SnapshotRestoreResponse.from_dict(each_page)

            except KeyError as e:
                raise e

        def cancel_snapshot_restore_request(self, cluster_name: str, restore_id: str):
            """
            Cancels a current backup restore request by restore_id.

            Calls:
            https://docs.atlas.mongodb.com/reference/api/cloud-backup/restore/delete-one-restore-job/

            Args:
                cluster_name: The name of the source cluster.
                restore_id:  The id of the (jobId) of the restore job.
            """
            # First Check if the restore_id is valid
            restore_info_result: SnapshotRestoreResponse = \
                self.get_snapshot_restore_requests(cluster_name=cluster_name, restore_id=restore_id, as_obj=True)
            restore_info = list(restore_info_result)[0]
            if not restore_info:
                raise ErrAtlasNotFound(404, {"error": f"The passed restore_id {restore_id} was not found"})

            elif restore_info.finished_at:
                raise ErrAtlasBadRequest(500,
                                         {"error": f"The passed restore_id ({restore_id} has already been completed"
                                                   f"and can not be canceled"})
            elif restore_info.cancelled is True:
                raise ErrAtlasConflict(500,
                                       {"error": f"The passed restore_id ({restore_id} has already been canceled"})

            else:
                uri = Settings.api_resources["Cloud Backup Restore Jobs"][
                    "Cancel manual download restore job by job_id"] \
                    .format(GROUP_ID=self.atlas.group, CLUSTER_NAME=cluster_name, JOB_ID=restore_id)
                logger.info(f'Preparing to cancel snapshot {restore_info.snapshot_id}, on'
                            f' {restore_info.target_cluster_name} with restore_id {restore_id}.')

                response = self.atlas.network.delete(Settings.BASE_URL + uri)

                return response

    class _Projects:
        """Atlas Projects

        see: https://www.mongodb.com/docs/atlas/reference/api/projects/

        The groups resource provides access to retrieve or create Atlas projects.

        groups is a synonym for projects throughout Atlas.

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        @property
        def projects(self) -> Iterable[Project]:
            """All Projects accessible by the current authed user/key
            Gets all projects for which the authed key has access.


            Returns (Iterable[Project]): Yields Project Objects.

            """

            uri = Settings.api_resources["Projects"]["Projects that the authenticated user can access"]

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e

            for each_page in response:
                for each_project in each_page.get('results'):
                    yield Project.from_dict(each_project)

        def _get_project(self, group_id: str = None, group_name: str = None) -> Project:
            """Returns a single Project
            Gets a single project, either by sending a group_id or a group name.

            Args:
                group_id (str): The unique identifier for the project.
                group_name (str): The user defined name for the project.

            Returns (Project): A Project Object.

            """
            if group_id and group_name:
                logger.error("Please pass either a group_id or a group_name, not both.")
                raise ValueError("Please pass either a group_id or a group_name, not both.")
            elif group_id:
                uri = Settings.api_resources["Projects"]["Project by group_id"].format(GROUP_ID=group_id)
            elif group_name:
                uri = Settings.api_resources["Projects"]["Project by group name"].format(GROUP_NAME=group_name)

            else:
                err_str = f"Please pass either a group_id or a group_name, you did not pass either. . ."
                logger.error(err_str)
                raise ValueError(err_str)

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e
            return_list = list()
            for each_page in response:
                return_list.append(Project.from_dict(each_page))
            return return_list[0]

        def project_by_name(self, project_name: str) -> Project:
            """Return project by name

            Args:
                project_name (str): The project name to return

            Returns (Project): A single Project

            """
            return self._get_project(group_name=project_name)

        def project_by_id(self, project_id: str) -> Project:
            """Return project by name

            Args:
                project_id (str): The project id (group_id) to return

            Returns (Project): A single Project

            """
            return self._get_project(group_id=project_id)

        def _group_id_select(self, group_id: str = None) -> str:
            """Returns either the passed group_id or the instantiated group_id.

            Args:
                group_id (str):

            Returns (str): The correct group_id to use.
            """
            if not group_id:
                if not self.atlas.group:
                    raise ValueError(
                        "You either pass a group_id when calling get_project_teams, or instantiate the atlas"
                        "instance with a group_id, you have neither.")
                else:
                    group_id = self.atlas.group
            else:
                if self.atlas.group != group_id:
                    logger.warning(f"You have over-ridden the instantiated group_id {self.atlas.group} with the passed"
                                   f"group_id {group_id}. This is allowed but may yield unexpected results!")
                else:
                    logger.info("You have passed a override group which is the same as the instantiated atlast group,"
                                "this will have no effect")
            return group_id

        def get_project_teams(self, group_id: str = None) -> Iterable[TeamRoles]:
            """Retrieves all teams assigned to the passed project/group

            Returns each team assigned to the project, along with the roles which are assigned.


            Returns (Iterable[TeamRoles]): Yields TeamRole Objects.
            """
            group_id = self._group_id_select(group_id)

            uri = Settings.api_resources["Projects"]["Project teams by group_id"].format(GROUP_ID=group_id)

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e

            for each_page in response:
                for each in each_page.get('results'):
                    yield TeamRoles(each.get("teamId"), each.get("roleNames"))

        @staticmethod
        def _process_user_options(uri: str, flatten_teams: bool, include_org_users: bool) -> str:
            """Helper method to append user options to uri.

            Args:
                uri:
                flatten_teams:
                include_org_users:

            Returns (str): The processed uri string.
            """
            if flatten_teams and include_org_users:
                uri = uri + f"?flattenTeams={flatten_teams}&includeOrgUsers={include_org_users}"
            elif flatten_teams:
                uri = uri + f"?flattenTeams={flatten_teams}"
            elif include_org_users:
                uri = uri + f"?includeOrgUsers={include_org_users}"
            return uri

        def get_project_users(self, group_id: str = None, flatten_teams: Optional[bool] = None,
                              include_org_users: Optional[bool] = None) -> Iterable[AtlasUser]:
            """Yields all users (AtlasUser objects) associated with the group_id.

            Args:
                flatten_teams Optional[bool]:
                group_id (str): The group id to search, will use the configured group for the Atlas instance if
                 instantiated in this way. flatten_teams (bool): Flag that indicates whether the returned list should
                 include users who belong to a team that is assigned a role in this project. You might not have
                 assigned the individual users a role in this project.
                include_org_users (bool): Flag that indicates whether the returned list should include users with
                 implicit access to the project through the Organization Owner or Organization Read Only role.
                 You might not have assigned the individual users a role in this project.


            Returns (Iterable[AtlasUser]: An iterable of AtlasUser objects.
            """
            group_id = self._group_id_select(group_id)
            uri = Settings.api_resources["Projects"]["Atlas Users assigned to project"].format(GROUP_ID=group_id)
            uri = self._process_user_options(uri, flatten_teams, include_org_users)

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e
            for each_page in response:
                for each in each_page.get('results'):
                    yield AtlasUser.from_dict(each)

        def user_count(self, group_id: str = None, flatten_teams: Optional[bool] = None,
                       include_org_users: Optional[bool] = None,
                       ) -> int:
            """Returns count of users added to this project

            Args:
                group_id (str): The group id to search, will use the configured group for the Atlas instance if
                instantiated in this way.
                flatten_teams (bool): Flag that indicates whether the returned list should include users who belong to a
                 team that is assigned a role in this project. You might not have assigned the individual users a role
                 in this project.
                include_org_users (bool): Flag that indicates whether the returned list should include users with
                 implicit access to the project through the Organization Owner or Organization Read Only role. You
                  might not have assigned the individual users a role in this project.


            Returns (int): Count of users.

            """
            group_id = self._group_id_select(group_id)
            uri = Settings.api_resources["Projects"]["Atlas Users assigned to project"].format(GROUP_ID=group_id)
            uri = self._process_user_options(uri, flatten_teams, include_org_users)

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e
            user_count = 0
            for each_page in response:
                for _ in each_page.get('results'):
                    user_count += 1
            logger.info(f"The user count is {user_count}")
            return user_count

        @property
        def settings(self) -> ProjectSettings:
            group_id = self.atlas.group
            uri = Settings.api_resources["Projects"]["Settings for project"].format(GROUP_ID=group_id)

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e

            return_list = list()
            for each_page in response:
                return_list.append(ProjectSettings.from_dict(each_page))
            return return_list[0]

    class _Organizations:
        """Atlas Organizations

               see: https://www.mongodb.com/docs/atlas/reference/api/organizations/

               TThe orgs resource provides access to manage Atlas organizations.

               Args:
                   atlas (Atlas): Atlas instance
               """

        def __init__(self, atlas):
            self.atlas = atlas

        def _get_orgs(self, org_name: str = None, org_id: str = None) -> Iterator[dict]:
            """Helper method for returning Org info from the API

            Args:
                org_name (str):  Organization name with which to filter the returned list. Performs a case-insensitive
                 search for organizations which exactly match the specified name.
                org_id (str): Specific org_id to return

            Returns (tuple): A tuple with results(array of dicts) and total count(int)

            """
            uri = Settings.api_resources["Organizations"]["Orgs the authenticated user can access"]
            if org_name:
                uri = uri + f"?name={org_name}"
            elif org_id:
                uri = uri + f"{org_id}"

            try:
                response = self.atlas.network.get(uri=Settings.BASE_URL + uri)
            except Exception as e:
                raise e

            if not org_id:
                for page in response:
                    for each in page.get("results"):
                        yield each
            else:
                for each in response:
                    yield each

        @property
        def organizations(self) -> Iterable[Organization]:
            """All Organizations accessible by the current authed user/key
            Gets all Organizations for which the authed key has access.


            Returns (Iterable[Organization]): Yields Organization Objects.

            """
            for each in self._get_orgs():
                yield Organization.from_dict(each)

        def organization_by_name(self, org_name: str) -> Organization:
            """Single organization searched by name.

            Args:
                org_name: Organization name with which to filter the returned list. Performs a case-insensitive
                 search for organizations which exactly match the specified name.

            Returns (Organization): a single Organization object.

            """
            return_list = []
            for each in self._get_orgs(org_name=org_name):
                return_list.append(each)
            return Organization.from_dict(return_list[0])

        def organization_by_id(self, org_id: str) -> Organization:
            """Single organization searched by org_id.

            Args:
                org_id (str):
            Returns (Organization): a single Organization object.

            """

            return_list = []
            for each in self._get_orgs(org_id=org_id):
                return_list.append(each)

            return Organization.from_dict(return_list[0])

        @property
        def count(self) -> int:
            """ Count of Organizations accessible by the authed user/key.

            Returns (int):

            """
            count = 0
            for each in self.organizations:
                count += 1
            return count

        def get_all_projects_for_org(self, org_id: str) -> Iterable[Project]:
            """Get projects related to the current Org

            url: https://www.mongodb.com/docs/atlas/reference/api/organization-get-all-projects/

            Args:
                org_id (str): The organization id which owns the projects.

            Returns:
                Iterable[Project]: Iterable containing projects


            """
            uri: str = Settings.api_resources["Organizations"]["Projects associated with the Org"].format(
                ORG_ID=org_id)

            response = self.atlas.network.get(Settings.BASE_URL + uri)
            for page in response:
                for each_project in page.get("results"):
                    yield Project.from_dict(each_project)

    class _Invoices:
        """Invoices API

        see: https://docs.atlas.mongodb.com/reference/api/invoices/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def count_for_org_id(self, org_id: str) -> int:
            """Returns the number of invoices available for the organization

            Args:
                org_id:

            Returns:
                int: count of invoices

            """
            uri = Settings.BASE_URL + Settings.api_resources["Invoices"][
                "Get All Invoices for One Organization"].format(ORG_ID=org_id)
            response = self.atlas.network.get(uri=uri, params={'includeCount': True})
            for page in response:
                logger.info(f"Total of {page.get('totalCount')} invoices to be returned")
                return page.get('totalCount')

        def get_all_for_org_id(self, org_id: str) -> Iterable[ApiInvoiceView]:
            """Returns all invoices available for the organization.

            Does not include detail for each invoice, you must get each invoice individually in get line items,
            and full details.
            Args:
                org_id:

            Returns:
                Iterable[ApiInvoiceView]: yields ApiInvoiceView objects
            """
            uri = Settings.BASE_URL + Settings.api_resources["Invoices"][
                "Get All Invoices for One Organization"].format(ORG_ID=org_id)
            response = self.atlas.network.get(uri=uri)
            for page in response:
                logger.info(f"Total of {page.get('totalCount')} invoices to be returned")
                for each_invoice in page.get("results"):
                    yield ApiInvoiceView.parse_obj(each_invoice)

        def get_pending_for_org_id(self, org_id: str) -> ApiInvoiceView:
            """Returns the single pending invoice for the organization.

            Args:
                org_id:

            Returns:
                ApiInvoiceView: A single Invoice

            """
            uri = Settings.BASE_URL + Settings.api_resources["Invoices"][
                "Get All Pending Invoices for One Organization"].format(ORG_ID=org_id)
            response = self.atlas.network.get(uri=uri)
            for page in response:
                return ApiInvoiceView.parse_obj(page)

        def get_single_invoice_for_org(self, org_id: str, invoice_id=str) -> ApiInvoiceView:
            """Returns a single invoice with all line items (Full Data).

            Args:
                org_id:
                invoice_id:

            Returns:
                ApiInvoiceView: A single invoice with all line items (Full Data).

            """
            uri = Settings.BASE_URL + Settings.api_resources["Invoices"][
                "Get One Organization Invoice"].format(ORG_ID=org_id, INVOICE_ID=invoice_id)
            response = self.atlas.network.get(uri=uri)
            for page in response:
                return ApiInvoiceView.parse_obj(page)

    class _Serverless:
        """Serverless API

        see: https://docs.atlas.mongodb.com/reference/api/serverless/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def get_group(self, group_id: Optional[str] = None):
            if self.atlas.group is None and group_id is None:
                raise AttributeError("A group/project id must be provided either in the Atlas object or as a parameter")
            elif self.atlas.group is not None and group_id is not None:
                raise AttributeError(f"You have provided a group_id ({group_id}) for an Atlas instance which was "
                                     f"instantiated with a group_id ({self.atlas.group}). Either use an Atlas"
                                     f"instance without a group_id, or do not specify the group_id as a parameter.")
            elif self.atlas.group is None and group_id is not None:
                logger.info(f"Using the passed group_id of {group_id}")

            else:
                logger.info(f"Using the Atlas instance group id of {self.atlas.group}")
                group_id = self.atlas.group
            return group_id

        def count_for_group_id(self, group_id: str) -> int:
            """Returns the number of serverless instances available for the project

            Args:
                group_id:

            Returns:
                int: count of serverless instances

            """
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Return All Serverless Instances"].format(GROUP_ID=group_id)
            response = self.atlas.network.get(uri=uri, params={'includeCount': True})
            for page in response:
                logger.info(f"Total of {page.get('totalCount')} serverless instances to be returned")
                return page.get('totalCount')

        @property
        def count(self) -> int:
            """Count of serverless instances for current project/group.

            Will only work if the Atlas object has been instantiated with a group/project id

            Returns:
                int:

            """
            if self.atlas.group is None:
                raise AttributeError(
                    'The Atlas object must be initialized with a project/group in order to use the `count` method.')
            else:
                return self.count_for_group_id(self.atlas.group)

        def get_all_for_project(self, group_id: str) -> Iterable[ServerlessInstance]:
            """Returns all serverless instances for the passed group.

            Args:
                group_id:

            Returns:
                Iterable[ServerlessInstance]: yields ApiInvoiceView objects
            """
            logger.info(f"The Atlas instance has a group defined {self.atlas.group}")
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Return All Serverless Instances"].format(GROUP_ID=group_id)
            response = self.atlas.network.get(uri=uri)
            for page in response:
                logger.info(f"Total of {page.get('totalCount')} serverless instances to be returned")
                for each_instance in page.get("results"):
                    yield ServerlessInstance.parse_obj(each_instance)

        @property
        def instances(self) -> Iterable[ServerlessInstance]:
            """Returns all serverless instances for the current project/group id.

            Will only work if the Atlas object has been instantiated with a group/project id.
            Returns:
                Iterable[ServerlessInstance]:
            """
            if self.atlas.group is None:
                raise AttributeError('The Atlas object must be initialized with a project/group in order to use the '
                                     '`instances` method.')
            else:
                return self.get_all_for_project(group_id=self.atlas.group)

        def get_one_for_project(self, group_id: str, instance_name: str) -> ServerlessInstance:
            """Returns a single Serverless Instance.

            Args:
                group_id:
                instance_name:

            Returns:
                ApiInvoiceView: A single invoice with all line items (Full Data).

            """
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Return One Serverless Instance"].format(GROUP_ID=group_id, INSTANCE_NAME=instance_name)
            response = self.atlas.network.get(uri=uri)
            for page in response:
                return ServerlessInstance.parse_obj(page)

        def instance(self, instance_name: str) -> ServerlessInstance:
            """Returns a single instance by instance_name

            Will only work if the Atlas object has been instantiated with a group/project id.


            Args:
                instance_name:

            Returns:
                ServerlessInstance:

            """
            if self.atlas.group is None:
                raise AttributeError('The Atlas object must be initialized with a project/group in order to use the '
                                     '`instance` method.')
            else:
                return self.get_one_for_project(group_id=self.atlas.group, instance_name=instance_name)

        def create(self, name: str, group_id: Optional[str] = None,
                   backing_provider: BackingProviderName = BackingProviderName.aws,
                   region_name: ServerlessRegionName = ServerlessRegionName.US_EAST_1,
                   continuous_backup: bool = False, termination_protection: bool = False) -> ServerlessInstance:
            """Creates a new serverless instance

            Only name is required, others have sane defaults.

            If the Altas instance is instantiated with a group, that group will be used, and you do not need to
            provide one as a parameter.

            If you provide a group and one is already intantiated, an error will be raised.

            Args:
                name:
                group_id:
                backing_provider:
                region_name:
                continuous_backup:
                termination_protection:

            Returns:
                ServerlessInstance:

            """
            group_id = self.get_group(group_id)

            provider_obj = ServerlessInstanceProviderSettings(backingProviderName=backing_provider,
                                                              providerName=ServerlessProviderName.serverless,
                                                              regionName=region_name
                                                              )
            backup_obj = {"serverlessContinuousBackupEnabled": continuous_backup}

            create_obj: ServerlessInstance = ServerlessInstance(groupId=group_id, name=name,
                                                                providerSettings=provider_obj,
                                                                serverlessBackupOptions=backup_obj,
                                                                terminationProtectionEnabled=termination_protection)

            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Create One Serverless Instance"].format(GROUP_ID=group_id, INSTANCE_NAME=name)

            payload_dict = loads(create_obj.json(by_alias=True, exclude_unset=True))

            instance_data = self.atlas.network.post(uri, payload=payload_dict)
            return ServerlessInstance.parse_obj(instance_data)

        def create_aws(self, name: str, group_id: Optional[str] = None,
                       region_name: ServerlessRegionName = ServerlessRegionName.US_EAST_1,
                       continuous_backup: bool = False, termination_protection: bool = False):
            """Little helper method for creating on aws.

            Args:
                name:
                group_id:
                region_name:
                continuous_backup:
                termination_protection:

            Returns:

            """
            group_id = self.get_group(group_id)
            return self.create(name=name, group_id=group_id, backing_provider=BackingProviderName.aws,
                               region_name=region_name, continuous_backup=continuous_backup,
                               termination_protection=termination_protection)

        def remove_one(self, name: str, group_id: Optional[str] = None) -> DeletedReturn:
            """
            Removes a single Serverless instance.

            You can pass None for the group/project id if the Atlas instance is instantiated with a group id.
            Args:
                name: the name of the instance as displayed in the UI and returned by GET
                group_id:

            Returns:
                DeletedReturn: A dist with 'deleted' either true or false.

            """
            group_id = self.get_group(group_id)
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Remove One Serverless Instance"].format(GROUP_ID=group_id, INSTANCE_NAME=name)

            return self.atlas.network.delete(uri)

        def delete(self, name: str) -> DeletedReturn:
            """
            Helper method to delete the named instance for the instantiated group id.

            Will fail if the Atlas object is not instantiated with a group/project id.

            Args:
                name (str):

            Returns:
                DeletedReturn
            """
            return self.remove_one(name)

        def update_continuous_backup(self, name: str, enabled: bool = False,
                                     group_id: Optional[str] = None) -> ServerlessInstance:
            """Enables or disables the continuous backup option.

            Args:
                group_id:
                name: Name of the instance to update
                enabled (bool): True to enable, False to disable.
            """
            group_id = self.get_group(group_id)
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Update One Serverless Instance"].format(GROUP_ID=group_id, INSTANCE_NAME=name)
            output = self.atlas.network.patch(uri, dict(serverlessContinuousBackupEnabled=enabled))
            return ServerlessInstance.parse_obj(output)

        def update_termination_protection(self, name: str, enabled: bool = False,
                                          group_id: Optional[str] = None) -> ServerlessInstance:
            """Enables or disables the termination protection option.

            Args:
                name (str): The name of the serverless instance
                enabled (bool):
                group_id (str):

            Returns:
                ServerlessInstance
            """
            group_id = self.get_group(group_id)
            uri = Settings.BASE_URL + Settings.api_resources["Serverless"][
                "Update One Serverless Instance"].format(GROUP_ID=group_id, INSTANCE_NAME=name)
            output = self.atlas.network.patch(uri, dict(terminationProtectionEnabled=enabled))
            return ServerlessInstance.parse_obj(output)

        def termination_protection_enable(self, name: str) -> ServerlessInstance:
            return self.update_termination_protection(name, True, None)

        def continuous_backup_enable(self, name: str) -> ServerlessInstance:
            return self.update_continuous_backup(name, True, None)


class AtlasPagination:
    """Atlas Pagination Generic Implementation

    Constructor

    Args:
        atlas (Atlas): Atlas instance
        fetch (function): The function "get_all" to call
        pageNum (int): Page number
        itemsPerPage (int): Number of Users per Page
    """

    def __init__(self, atlas, fetch, pageNum: int, itemsPerPage: int):
        self.atlas = atlas
        self.fetch = fetch
        self.pageNum = pageNum
        self.itemsPerPage = itemsPerPage

    def __iter__(self):
        """Iterable

        Yields:
            str: One result
        """

        # pageNum is set with the value requested (so not necessary 1)
        pageNum = self.pageNum
        # total: This is a fake value to enter into the while. It will be updated with a real value later
        total = pageNum * self.itemsPerPage

        while pageNum * self.itemsPerPage - total < self.itemsPerPage:
            # fetch the API
            try:
                details = self.fetch(pageNum, self.itemsPerPage)
            except Exception as e:
                raise ErrPagination(e)

            # set the real total
            total = details["totalCount"]

            # while into the page results
            results = details["results"]
            results_count = len(results)
            index = 0
            while index < results_count:
                result = results[index]
                index += 1
                yield result

            class DatabaseUsersGetAll(AtlasPagination):
                """Pagination for Database User : Get All"""

                def __init__(self, atlas, pageNum, itemsPerPage):
                    super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)

            # next page
            pageNum += 1


# noinspection PyProtectedMember
class DatabaseUsersGetAll(AtlasPagination):
    """Pagination for Database User : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.DatabaseUsers.get_all_database_users, pageNum, itemsPerPage)


class AlertsGetAll(AtlasPagination):
    """Pagination for Alerts : Get All"""

    def __init__(self, atlas, status, pageNum, itemsPerPage):
        super().__init__(atlas, self.fetch, pageNum, itemsPerPage)
        self.get_all_alerts = atlas.Alerts.get_all_alerts
        self.status = status

    def fetch(self, pageNum, itemsPerPage):
        """Intermediate fetching

        Args:
            pageNum (int): Page number
            itemsPerPage (int): Number of Users per Page

        Returns:
            dict: Response payload
        """
        return self.get_all_alerts(self.status, pageNum, itemsPerPage)


class WhitelistGetAll(AtlasPagination):
    """Pagination for Database User : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Whitelist.get_all_whitelist_entries, pageNum, itemsPerPage)
