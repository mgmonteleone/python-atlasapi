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

"""
Atlas module

Core module which provides access to MongoDB Atlas Cloud Provider APIs
"""
from .settings import Settings
from .network import Network
from .errors import *

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from .specs import Host, ListOfHosts, DatabaseUsersUpdatePermissionsSpecs, DatabaseUsersPermissionsSpecs
from typing import Union, Iterator, List, Optional
from .atlas_types import OptionalInt, OptionalBool, ListofDict
from .clusters import ClusterConfig, ShardedClusterConfig, AtlasBasicReplicaSet, \
    MongoDBMajorVersion, InstanceSizeName, ProviderName, AdvancedOptions
from .lib import AtlasPeriods, AtlasGranularities, AtlasUnits
from atlasapi.measurements import AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement, \
    OptionalAtlasMeasurement
from atlasapi.events import atlas_event_factory, ListOfEvents
import logging
from typing import Union, Iterable, Set, BinaryIO
from atlasapi.errors import ErrAtlasUnauthorized
from atlasapi.alerts import Alert
from time import time
from atlasapi.whitelist import WhitelistEntry
from atlasapi.maintenance_window import MaintenanceWindow, Weekdays
from atlasapi.lib import AtlasLogNames, LogLine
from requests import get
import gzip

logger = logging.getLogger('Atlas')


# noinspection PyProtectedMember
class Atlas:
    """Atlas constructor
    
    Args:
        user (str): Atlas user
        password (str): Atlas password
        group (str): Atlas group
    """

    def __init__(self, user, password, group):
        self.group = group

        # Network calls which will handled user/password for auth
        self.network = Network(user, password)

        # APIs
        self.DatabaseUsers = Atlas._DatabaseUsers(self)
        self.Clusters = Atlas._Clusters(self)
        self.Hosts = Atlas._Hosts(self)
        self.Events = Atlas._Events(self)
        self.logger = logging.getLogger(name='Atlas')
        self.Alerts = Atlas._Alerts(self)
        self.Whitelist = Atlas._Whitelist(self)
        self.MaintenanceWindows = Atlas._MaintenanceWindows(self)

    class _Clusters:
        """Clusters API

        see: https://docs.atlas.mongodb.com/reference/api/clusters/

        Constructor

        Args:
            atlas (Atlas): Atlas instance
        """

        def __init__(self, atlas):
            self.atlas = atlas

        def is_existing_cluster(self, cluster):
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

        def get_all_clusters(self, pageNum=Settings.pageNum, itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get All Clusters

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-all/

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
                return ClustersGetAll(self.atlas, pageNum, itemsPerPage)

            uri = Settings.api_resources["Clusters"]["Get All Clusters"] % (self.atlas.group, pageNum, itemsPerPage)
            return self.atlas.network.get(Settings.BASE_URL + uri)

        def get_single_cluster(self, cluster: str) -> dict:
            """Get a Single Cluster

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/

            Args:
                cluster (str): The cluster name

            Returns:
                dict: Response payload
            """
            uri = Settings.api_resources["Clusters"]["Get a Single Cluster"] % (self.atlas.group, cluster)
            cluster_data = self.atlas.network.get(Settings.BASE_URL + uri)
            return cluster_data

        def get_single_cluster_advanced_options(self, cluster: str, as_obj: bool = True) -> Union[dict,
                                                                                                  AdvancedOptions]:
            """
            Retrieves advanced options from a cluster, either as a obj, or optionally as a dict.

            GET /groups/{GROUP-ID}/clusters/{CLUSTER-NAME}/processArgs

            :param cluster:
            :param as_obj: True to return, AdvancedOptions, false for a dict
            :return: AdvancedOptions object or dict
            """
            uri = Settings.api_resources["Clusters"]["Advanced Configuration Options"].format(GROUP_ID=self.atlas.group,
                                                                                              CLUSTER_NAME=cluster)
            advanced_options = self.atlas.network.get(Settings.BASE_URL + uri)

            if as_obj is True:
                return_obj = AdvancedOptions.fill_from_dict(data_dict=advanced_options)
            else:
                return_obj = advanced_options

            return return_obj

        def get_single_cluster_as_obj(self, cluster) -> Union[ClusterConfig, ShardedClusterConfig]:
            """Get a Single Cluster as data

            url: https://docs.atlas.mongodb.com/reference/api/clusters-get-one/

            Args:
                cluster (str): The cluster name

            Returns:
                ClusterConfig: Response payload
            """
            cluster_data = self.get_single_cluster(cluster=cluster)
            try:
                if cluster_data.get('clusterType', None) == 'SHARDED':
                    logger.info("Cluster Type is SHARDED, Returning a ShardedClusterConfig")
                    out_obj = ShardedClusterConfig.fill_from_dict(data_dict=cluster_data)
                elif cluster_data.get('clusterType', None) == 'REPLICASET':
                    logger.info("Cluster Type is REPLICASET, Returning a ClusterConfig")
                    out_obj = ClusterConfig.fill_from_dict(data_dict=cluster_data)
                else:
                    logger.info("Cluster Type is not recognized, Returning a REPLICASET")
                    out_obj = ClusterConfig.fill_from_dict(data_dict=cluster_data)
            except Exception as e:
                raise e
            return out_obj

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
                    "Please set areYouSure=True on delete_a_cluster call if you really want to delete [%s]" % cluster)

        def modify_cluster(self, cluster: str, cluster_config: Union[ClusterConfig, dict]) -> dict:
            """Modify a Cluster

            Modifies an existing cluster in the project. Either from a full ClusterConfig object, or from a simple
            dict which contains the elements desired.


            url: https://docs.atlas.mongodb.com/reference/api/clusters-modify-one/


            :param cluster: The name of the cluster to modify
            :param cluster_config: A ClusterConfig object containing the new configuration,
                                   or a dict containing fragment.
            :return: dict:  A dictionary of the new cluster config
            TODO: Option to return a cluster config object
            """
            uri = Settings.api_resources["Clusters"]["Modify a Cluster"].format(GROUP_ID=self.atlas.group,
                                                                                CLUSTER_NAME=cluster)
            try:
                self.get_single_cluster_as_obj(cluster=cluster)
            except ErrAtlasNotFound:
                logger.error('Could not find existing cluster {}'.format(cluster))
                raise ValueError('Could not find existing cluster {}'.format(cluster))

            if type(cluster_config) == ClusterConfig:
                logger.warning("We received a full cluster_config, converting to dict")
                try:
                    new_config = cluster_config.as_modify_dict()
                except Exception as e:
                    logger.error('Error while trying to parse the new configuration')
                    raise e
            else:
                logger.warning("We received a simple dict for cluster config, sending without converting.")
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
                                            as_obj: bool = True) -> Union[AdvancedOptions, dict]:
            """
            Modifies cluster advanced options using a AdvancedOptions object.

            PATCH /groups/{GROUP-ID}/clusters/{CLUSTER-NAME}/processArgs

            :param cluster: The clutster name
            :param advanced_options: An AdvancedOptions object with the options to be set.
            :param as_obj: Return the new AdvancedOptions as an object.
            :return:
            """
            uri = Settings.api_resources["Clusters"]["Advanced Configuration Options"].format(GROUP_ID=self.atlas.group,
                                                                                              CLUSTER_NAME=cluster)

            value_returned = self.atlas.network.patch(uri=Settings.BASE_URL + uri, payload=advanced_options.as_dict)

            if as_obj is True:
                return_obj = AdvancedOptions.fill_from_dict(data_dict=value_returned)
            else:
                return_obj = value_returned

            return return_obj

        def pause_cluster(self, cluster: str, toggle_if_paused: bool = False) -> dict:
            """
            Pauses/Unpauses a cluster.

            If you wish to unpause, set the toggle_if_paused param to True.
            :rtype: dict
            :param cluster: The name of the cluster
            :param toggle_if_paused: Set to true to unpause a paused clsuter.
            :return: dict: The updated config
            """
            existing_config = self.get_single_cluster_as_obj(cluster=cluster)
            logger.info('The cluster state is currently Paused= {}'.format(existing_config.paused))
            if existing_config.paused is True and toggle_if_paused is False:
                logger.error("The cluster is already paused. Use unpause instead.")
                raise ErrAtlasBadRequest(400,
                                         {'msg': 'The cluster is already paused. Use toggle_if_paused to unpause.'})
            elif existing_config.paused is True and toggle_if_paused is True:
                logger.warning('Cluster is paused, will toggle to unpaused, since toggle_if paused is true')
                new_config = dict(paused=False)
            else:
                new_config = dict(paused=True)
            return self.modify_cluster(cluster=cluster, cluster_config=new_config)

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
            self.atlas = atlas
            self.logger = logging.getLogger('Atlas.Hosts')
            self.host_list_with_measurements: Optional[List[Host]] = list()
            self.host_list: Optional[List[Host]] = list()

        def _get_all_hosts(self, pageNum=Settings.pageNum,
                           itemsPerPage=Settings.itemsPerPage,
                           iterable=False):
            """Get All Hosts (actually processes)

            Internal use only, actual data retrieval comes from properties host_list and host_names
            url: https://docs.atlas.mongodb.com/reference/api/alerts-get-all-alerts/

            Keyword Args:
                pageNum (int): Page number
                itemsPerPage (int): Number of Users per Page
                iterable (bool): To return an iterable high level object instead of a low level API response

            Returns:
                ListOfHosts or dict: Iterable object representing this function OR Response payload

            Raises:
                ErrPaginationLimits: Out of limits
                :rtype: Union[ListOfHosts, dict]
                :type iterable: OptionalBool
                :type itemsPerPage: OptionalInt
                :type pageNum: OptionalInt

            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            if iterable:
                item_list = list(HostsGetAll(self.atlas, pageNum, itemsPerPage))
                obj_list = list()
                for item in item_list:
                    obj_list.append(Host(item))
                return_val = obj_list
            else:
                uri = Settings.api_resources["Monitoring and Logs"]["Get all processes for group"].format(
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage)

                return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            return return_val

        def fill_host_list(self, for_cluster: Optional[str] = None) -> ListOfHosts:
            """
            Fills the `self.hostname` property with the current hosts for the project/group.

            Optionally, one can specify the `for_cluster` parameter to fill the host list with
            hosts only from the specified cluster.

            :param for_cluster: str: The name of the cluster for filter the host list.
            """
            host_list = self._get_all_hosts(iterable=True)
            if for_cluster:
                out_list = list()
                for host in host_list:
                    if host.cluster_name == for_cluster:
                        out_list.append(host)
                self.host_list = out_list
            else:
                self.host_list = self._get_all_hosts(iterable=True)

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


            This is done by parsing the hostnames of the hosts, so any changes to that logic will break this.
            """
            cluster_list = set()
            for host in self.host_list:
                cluster_list.add(host.cluster_name)
            return cluster_list

        def host_list_by_cluster(self, cluster_name: str) -> Iterable[Host]:
            """
            Returns hosts belonging to the named cluster.
            :param cluster_name:
            """
            for host in self.host_list:
                if host.cluster_name == cluster_name:
                    yield host

        def update_host_list(self, host_obj: Host) -> None:
            """
            Replaces a host into the host_list property.

            Returns boolean indicating if the object was replaced.
            :rtype: bool
            :param host_obj: Host: A host object ith measurements.
            """
            for n, i in enumerate(self.host_list):
                if i == host_obj:
                    self.host_list[n] = host_obj
            self.logger.info("Added new host item")

        def get_measurement_for_hosts(self, granularity: AtlasGranularities = AtlasGranularities.HOUR,
                                      period: AtlasPeriods = AtlasPeriods.WEEKS_1,
                                      measurement=AtlasMeasurementTypes.Cache.dirty, return_data: bool = False):
            """Get  measurement(s) for all hosts in the host_list


                        Populates all hosts in the host_list with the requested metric.

                        Multiple calls will append additional metrics to the same host object.

                        Please note that using the `return_data`  param will also return the updated
                        host objects, which may unnecessarily consume memory.

                        Keyword Args:
                            granularity (AtlasGranuarities): the desired granularity
                            period (AtlasPeriods): The desired period
                            measurement (AtlasMeasurementTypes) : The desired measurement or Measurement class



                            :param return_data:
                            :rtype: List[AtlasMeasurement]
                            :type period: AtlasPeriods
                            :type granularity: AtlasGranularities
                            :type measurement: AtlasMeasurementTypes
                        """

            if not self.host_list:
                raise (ValueError('Before retrieving measurements for hosts, you must retrieve the host list'
                                  ' by using one of the `fill_host_list`.'))

            for each_host in self.host_list:
                logger.info('Pulling measurements for {} hosts'.format(len(self.host_list)))
                logger.info('Measurement: {}'.format(measurement.__str__()))
                logger.info('Metric: {}'.format(granularity.__str__()))
                logger.info('For Period: {}'.format(period.__str__()))
                return_list = list()
                try:
                    returned_data = self._get_measurement_for_host(each_host, granularity=granularity,
                                                                   period=period,
                                                                   measurement=measurement)
                    return_list.append(returned_data)
                except Exception as e:
                    logger.error('An error occurred while retrieving metrics for host: {}.'
                                 'The error was {}'.format(each_host.hostname, e))
                    logger.warning('Will continue with next host. . . ')

        def get_log_for_host(self, host_obj: Host,
                             log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                             date_from: datetime = None,
                             date_to: datetime = None,
                             ) -> BinaryIO:
            """
            Retrieves the designated logfile archive of designated log_name and for the designated dates,
            and returns a binary file like object.
            Args:
                host_obj: And atlas Host object to retrieve logs for
                log_name: an AtlasLogNames type
                date_from: The datetime to start from
                date_to: The datetime to gather till

            Returns: A BinaryIO object containing the gzipped log file.

            """
            uri = Settings.api_resources["Monitoring and Logs"]["Get the log file for a host in the cluster"].format(
                group_id=self.atlas.group,
                host=host_obj.hostname,
                logname=log_name.value,
                date_from=date_from,
                date_to=date_to
            )
            # Build the request
            if date_to is None and date_from is None:
                logger.info('No dates passed so we are not going to send date params, API default will be used.')
                uri = Settings.BASE_URL + uri
            elif date_to is None and date_from is not None:
                logger.info('Received only a date_from, so sending only startDate')
                uri = Settings.BASE_URL + uri + f'?startDate={int(round(date_from.timestamp()))}'
            elif date_to is not None and date_from is None:
                uri = Settings.BASE_URL + uri + f'?endDate={int(round(date_to.timestamp()))}'
            else:
                uri = Settings.BASE_URL + uri + f'?endDate={int(round(date_to.timestamp()))}' \
                                                f'&startDate={int(round(date_from.timestamp()))}'
            logger.info(f'The URI used will be {uri}')
            return_val = self.atlas.network.get_file(uri)
            return return_val

        def get_loglines_for_host(self, host_obj: Host,
                                  log_name: AtlasLogNames = AtlasLogNames.MONGODB,
                                  date_from: datetime = None,
                                  date_to: datetime = None,
                                  ) -> Iterable[LogLine]:
            """
            Gathers the designated log file from Atlas, and then returns the lines therin contained.

            Args:
                host_obj: And atlas Host object to retrive logs for
                log_name: an AtlasLogNames type
                date_from: The datetime to start from
                date_to: The datetime to gather till
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
            Yields File-like objects containing the gzipped log file requested for each and every host in the project
            using the same date filters and log_name (type)
            Args:
                log_name: AtlasLognames: The type of log to be retrieved
                date_from: datetime : Start of log entries
                date_to: datetime: End of log entries

            Returns:
                Iterable[BinaryIO]: An iterable of file-like objects.
            """
            for each_host in self.host_list:
                try:
                    log_file: BinaryIO = self.get_log_for_host(host_obj=each_host,
                                                               log_name=log_name,
                                                               date_from=date_from,
                                                               date_to=date_to)
                except Exception as e:
                    raise e
                each_host.add_log_file(name=log_name,file=log_file)
                yield each_host

        def _get_measurement_for_host(self, host_obj: Host, granularity: AtlasGranularities = AtlasGranularities.HOUR,
                                      period: AtlasPeriods = AtlasPeriods.WEEKS_1,
                                      measurement: AtlasMeasurementTypes = AtlasMeasurementTypes.Cache.dirty,
                                      pageNum: int = Settings.pageNum,
                                      itemsPerPage: int = Settings.itemsPerPage,
                                      iterable: bool = True) -> Union[dict, Iterable[AtlasMeasurement]]:
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

                :rtype: List[AtlasMeasurement]
                :type iterable: OptionalBool
                :type itemsPerPage: OptionalInt
                :type pageNum: OptionalInt
                :type period: AtlasPeriods
                :type granularity: AtlasGranularities
                :type host_obj: Host
                :type measurement: AtlasMeasurementTypes

            """

            # Check limits and raise an Exception if needed
            ErrPaginationLimits.checkAndRaise(pageNum, itemsPerPage)

            # Check to see if we received a leaf or branch of the measurements
            try:
                parent = super(measurement)
                self.logger.info('We received a branch, whos parent is {}'.format(parent.__str__()))
                leaves = measurement.get_all()
                measurement_list = list(leaves)
                measurement = '&m='.join(measurement_list)
            except TypeError:
                self.logger.info('We received a leaf')

            # Build the URL
            uri = Settings.api_resources["Monitoring and Logs"]["Get measurement for host"].format(
                group_id=self.atlas.group,
                host=host_obj.hostname,
                port=host_obj.port,
                granularity=granularity,
                period=period,
                measurement=measurement
            )
            # Build the request
            return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            if iterable:
                measurements = return_val.get('measurements')
                measurements_count = len(measurements)
                self.logger.info('There are {} measurements.'.format(measurements_count))

                for each in measurements:
                    measurement_obj = AtlasMeasurement(name=each.get('name'),
                                                       period=period,
                                                       granularity=granularity)
                    for each_and_every in each.get('dataPoints'):
                        measurement_obj.measurements = AtlasMeasurementValue(each_and_every)

                yield measurement_obj

            else:
                return return_val

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

        def _get_all_project_events(self, pageNum: int = Settings.pageNum,
                                    itemsPerPage: int = Settings.itemsPerPage,
                                    iterable: bool = False) -> ListOfEvents:
            """Get All Project Events

            Internal use only, actual data retrieval comes from properties events_list
            url: https://docs.atlas.mongodb.com/reference/api/events-projects-get-all/

            Keyword Args:
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
                item_list = list(EventsGetForProject(self.atlas, pageNum, itemsPerPage))
                obj_list = list()
                for item in item_list:
                    obj_list.append(atlas_event_factory(item))
                return_val = obj_list
            else:
                uri = Settings.api_resources["Events"]["Get All Project Events"].format(
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage)

                return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            return return_val

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
            (Internal)Gets the current maint window configuration for the the project.

            the current_config should be used instead.

            Args:
                as_obj: Return data as a MaintenanceWindowObj

            Returns:

            """
            uri = Settings.api_resources["Maintenance Windows"]["Get Maintenance Window"].format(
                GROUP_ID=self.atlas.group)
            response = self.atlas.network.get(Settings.BASE_URL + uri)
            if as_obj is False:
                return response
            else:
                return MaintenanceWindow.from_dict(response)

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

            Will only set those values which are not none in the MaintWindow Object. Currently you can not use
            this method to set a value as null. (This is not supported by the API anyway)

            Args:
                new_config: A MaintainenceWindow Object

            Returns: bool: True is success

            """
            output: bool = self._update_maint_window(new_config=new_config)
            return output


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
            except Exception:
                raise ErrPagination()

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


class ClustersGetAll(AtlasPagination):
    """Pagination for Clusters : Get All"""

    def __init__(self, atlas, pageNum, itemsPerPage):
        super().__init__(atlas, atlas.Clusters.get_all_clusters, pageNum, itemsPerPage)


# noinspection PyProtectedMember
class HostsGetAll(AtlasPagination):
    """Pagination for Processes : Get All"""

    def __init__(self, atlas: Atlas, pageNum: int, itemsPerPage: int):
        super().__init__(atlas, atlas.Hosts._get_all_hosts, pageNum, itemsPerPage)


# noinspection PyProtectedMember
class EventsGetForProject(AtlasPagination):

    def __init__(self, atlas: Atlas, pageNum: int, itemsPerPage: int):
        super().__init__(atlas, atlas.Events._get_all_project_events, pageNum, itemsPerPage)


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
