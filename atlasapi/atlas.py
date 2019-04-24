# Copyright (c) 2018 Yellow Pages Inc.
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
from .specs import Host, ListOfHosts
from typing import Union, Iterator
from .atlas_types import OptionalInt, OptionalBool, ListofDict
from .lib import AtlasPeriods, AtlasGranularities, AtlasUnits
from atlasapi.measurements import AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement, \
    OptionalAtlasMeasurement
import logging
from pprint import pprint


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
        self.Hosts = Atlas._Hosts(self)
        self.logger = logging.getLogger(name='Atlas')

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

        @property
        def host_list(self):
            """Returns a list of Host Objects
            :rtype: ListOfHosts
            """

            return self._get_all_hosts(iterable=True)

        @property
        def host_names(self):
            """Returns a simple list of host names without port
            :rtype: Iterator[str]
            """

            for host in self.host_list:
                yield host.hostname

        def _get_measurement_for_host(self, host_obj, granularity=AtlasGranularities.HOUR, period=AtlasPeriods.WEEKS_1,
                                      measurement=AtlasMeasurementTypes.Cache.dirty, pageNum=Settings.pageNum,
                                      itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get  measurement(s_ for a host

            Internal use only, should come from the host obj itself.
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
                 List[AtlasMeasurement] or dict: Iterable object representing this function OR Response payload

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
            except TypeError as e:
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
                self.logger.warning('There are {} measurements.'.format(measurements_count))
                measurements_list = list()

                for each in measurements:
                    measurement_obj = AtlasMeasurement(name=each.get('name')
                                                       , period=period
                                                       , granularity=granularity)
                    for each_and_every in each.get('dataPoints'):
                        measurement_obj.measurements = AtlasMeasurementValue(each_and_every)
                    measurements_list.append(measurement_obj)
                return measurements_list

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
            self.atlas = atlas
            self.logger = logging.getLogger('Atlas.Events')

        def _get_all_project_events(self, pageNum=Settings.pageNum,
                           itemsPerPage=Settings.itemsPerPage,
                           iterable=False):
            """Get All Project Events (actually processes)

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
                item_list = list(ProjectEventsGetAll(self.atlas, pageNum, itemsPerPage))
                obj_list = list()
                for item in item_list:
                    obj_list.append(Event(item))
                return_val = obj_list
            else:
                uri = Settings.api_resources["Events"]["Get All Project Events"].format(
                    group_id=self.atlas.group,
                    page_num=pageNum,
                    items_per_page=itemsPerPage)

                return_val = self.atlas.network.get(Settings.BASE_URL + uri)

            return return_val

        @property
        def host_list(self):
            """Returns a list of Host Objects
            :rtype: ListOfHosts
            """

            return self._get_all_hosts(iterable=True)

        @property
        def host_names(self):
            """Returns a simple list of host names without port
            :rtype: Iterator[str]
            """

            for host in self.host_list:
                yield host.hostname

        def _get_measurement_for_host(self, host_obj, granularity=AtlasGranularities.HOUR,
                                      period=AtlasPeriods.WEEKS_1,
                                      measurement=AtlasMeasurementTypes.Cache.dirty, pageNum=Settings.pageNum,
                                      itemsPerPage=Settings.itemsPerPage, iterable=False):
            """Get  measurement(s_ for a host

            Internal use only, should come from the host obj itself.
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
                 List[AtlasMeasurement] or dict: Iterable object representing this function OR Response payload

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
            except TypeError as e:
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
                measurements_list = list()

                for each in measurements:
                    measurement_obj = AtlasMeasurement(name=each.get('name')
                                                       , period=period
                                                       , granularity=granularity)
                    for each_and_every in each.get('dataPoints'):
                        measurement_obj.measurements = AtlasMeasurementValue(each_and_every)
                    measurements_list.append(measurement_obj)
                return measurements_list

            else:
                return return_val


class AtlasPagination:
    """Atlas Pagination Generic Implementation
    
    Constructor
        
    Args:
        atlas (Atlas): Atlas instance
        fetch (function): The function "get_all" to call
        pageNum (int): Page number
        itemsPerPage (int): Number of Users per Page
    """

    def __init__(self, atlas, fetch, pageNum, itemsPerPage):
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

            # next page
            pageNum += 1


# noinspection PyProtectedMember
class HostsGetAll(AtlasPagination):
    """Pagination for Processes : Get All"""

    def __init__(self, atlas: Atlas, pageNum: int, itemsPerPage: int):
        super().__init__(atlas, atlas.Hosts._get_all_hosts, pageNum, itemsPerPage)
