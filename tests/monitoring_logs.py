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
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from atlasapi.measurements import AtlasMeasurementTypes

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER,API_KEY,GROUP_ID)

# Low level Api
#details = a.Hosts._get_all_hosts(pageNum=1, itemsPerPage=100)
#pprint(details)
#print('-----------------Now as iterable ------------------')
# Iterable
#for a_host in a.Hosts.host_names:
#    print(a_host)

pprint('----------MeasureMents')
output = a.Hosts._get_measurement_for_host(a.Hosts.host_list[0]
                                           ,measurement=AtlasMeasurementTypes.Memory.virtual,iterable=True
                                           ,period=AtlasPeriods.HOURS_24,granularity=AtlasGranularities.MINUTE)

for each in output[0].measurements:
    pprint(each.__dict__)
pprint('------------Test list of clusters-----------------')

cluster_list = a.Hosts.cluster_list

for cluster in cluster_list:
    print('Cluster name {}'.format(cluster))


pprint('------------Test get hosts by cluster-----------------')

hosts = a.Hosts.host_list_by_cluster('monitoringtest')

for hosts in hosts:
    pprint(hosts.__dict__)