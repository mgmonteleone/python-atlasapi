# Copyright (c) 2019 Joe Drumgoole
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
# Modifications copyright (C) Joe Drumgoole

from enum import Enum
import pprint


class ListFormat(Enum):
    short = "short"
    full = "full"

    def __str__(self):
        return self.value


class Commands(Enum):
    List = "List"

    def __str__(self):
        return self.value


class ListCommand:
    """
    Execute the list command
    """

    def __init__(self, format: ListFormat = ListFormat.short):
        self._format = format

    def list_one(self, resource):
        if self._format is ListFormat.short:
            print(resource["id"])
        else:
            pprint.pprint(resource)

    def list_all(self, iterator):
        counter = 0
        for counter, resource in enumerate(iterator):
            self.list_one(resource)
        return counter
