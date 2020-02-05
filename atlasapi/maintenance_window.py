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
Maint Window Module

The maintenanceWindow resource provides access to retrieve or update the current Atlas project maintenance window.
To learn more about Maintenance Windows, see the Set Preferred Cluster Maintenance Start Time
setting on the View/Modify Project Settings page.

"""
from enum import Enum
from pprint import pprint
import logging
from json import dumps
from enum import IntEnum

logger = logging.getLogger('maintenance_window')


class Weekdays(Enum):
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7


class MaintenanceWindow(object):
    def __init__(self, day_of_week: Weekdays = Weekdays.SUNDAY, hour_of_day: int = 23, number_of_deferrals: int = 1,
                 start_asap: bool = False):
        """
        Stores the definition of maint window configuration for a group/project.

        Args:
            day_of_week: The day of week that maint should run
            hour_of_day: the hour of the day (24 based) to run maint
            number_of_deferrals:
            start_asap:
        """
        self.startASAP = start_asap
        self.numberOfDeferrals = number_of_deferrals
        self.hourOfDay = hour_of_day
        self.dayOfWeek = day_of_week

    @classmethod
    def from_dict(cls, data_dict: dict):
        """
        Creates a maint window definition from a dict.
        Args:
            data_dict: An atlas formated dict

        Returns:

        """
        day_of_week: Weekdays = Weekdays(data_dict.get('dayOfWeek', None))
        hour_of_day = data_dict.get('hourOfDay', None)
        number_of_deferrals = data_dict.get('numberOfDeferrals', None)
        start_asap = data_dict.get('startASAP', None)

        return cls(day_of_week, hour_of_day, number_of_deferrals, start_asap)

    def as_dict(self) -> dict:
        """
        Returns the Maintenance object as a serializable dict

        Converts enums
        Returns:

        """
        out_dict = self.__dict__
        if type(out_dict['dayOfWeek']) == Weekdays:
            out_dict['dayOfWeek'] = out_dict['dayOfWeek'].value
        return out_dict

    def as_update_dict(self) -> dict:
        """
        Returns a dict with immutable properties removed.
        Returns: dict
        """
        update_dict = self.as_dict()
        del update_dict['numberOfDeferrals']
        for key, val in update_dict.items():
            if val is None:
                del update_dict[key]


        return update_dict
