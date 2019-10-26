# Copyright (c) 20109 Matthew G. Monteleone
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
Stupid and simple smoke tests.

Uses ENV vars to store user, key and group.

TODO: Create real tests


"""

from atlasapi.atlas import Atlas
from pprint import pprint
from os import environ, getenv

from atlasapi.specs import ListOfHosts, Host
USER = getenv('ATLAS_USER', 'JKKIDWUA')
API_KEY = getenv('ATLAS_KEY', '4e09ab9f-bf2c-41da-90bf-7d7974c330d2')
GROUP_ID = getenv('ATLAS_GROUP', '5b1e92c13b34b93b0230e6e1')
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from atlasapi.measurements import AtlasMeasurementTypes

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER,API_KEY,GROUP_ID)


pprint('----------MeasureMents')
output = a.Hosts._get_measurement_for_host(a.Hosts.host_list[0]
                                           ,measurement=AtlasMeasurementTypes.Memory.resident,iterable=True
                                           ,period=AtlasPeriods.WEEKS_4,granularity=AtlasGranularities.MINUTE)

for each in a.Hosts.host_list:
    pprint(each.__dict__)
