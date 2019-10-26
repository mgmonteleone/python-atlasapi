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
from atlasapi.atlas import Atlas
from json import dumps


from atlasapi.specs import DatabaseUsersPermissionsSpecs, RoleSpecs, DatabaseUsersUpdatePermissionsSpecs

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER, API_KEY, GROUP_ID)


#print('----------Test Get whitelist entries------------------')
#
#
#out = a.Whitelist.get_all_whitelist_entries()
#
#for each in out:
#    pprint(each.__dict__)
#

print('----------Create a whitelist entry then get it.------------------')


#returnit = a.Whitelist.create_whitelist_entry('67.180.12.52', 'Test 12')

out = a.Whitelist.get_whitelist_entry('67.180.12.52')

pprint(out.__dict__)
