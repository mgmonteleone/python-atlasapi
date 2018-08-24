"""
Stupid and simple smoke tests.

Uses ENV vars to store user, key and group.

TODO: Create real tests


"""

from atlasapi.atlas import Atlas
from pprint import pprint
from os import environ, getenv
from atlasapi.specs import ListOfHosts, Host
USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER,API_KEY,GROUP_ID)

# Low level Api
details = a.Hosts._get_all_hosts(pageNum=1, itemsPerPage=100)
pprint(details)
print('-----------------Now as iterable ------------------')
# Iterable
for a_host in a.Hosts.host_names:
    print(a_host)