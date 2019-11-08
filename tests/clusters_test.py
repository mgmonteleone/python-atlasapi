"""
Stupid and simple smoke tests.

Uses ENV vars to store user, key and group.

TODO: Create real tests


"""

from atlasapi.atlas import Atlas
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from json import dumps
from atlasapi.clusters import AtlasBasicReplicaSet, MongoDBMajorVersion as mdb_version, ClusterConfig
from atlasapi.clusters import ClusterConfig, ProviderSettings, ReplicationSpecs
from atlasapi.clusters import RegionConfig

USER = getenv('ATLAS_USER', None)
API_KEY = getenv('ATLAS_KEY', None)
GROUP_ID = getenv('ATLAS_GROUP', None)

TEST_CLUSTER_NAME = 'pyAtlasAPIClustersTest'

if not USER or not API_KEY or not GROUP_ID:
    raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                           'your env variables are {}'.format(environ.__str__()))

a = Atlas(USER, API_KEY, GROUP_ID)

## Get All Clusters
# pprint('===========Get All Clusters==========')
# for cluster in a.Clusters.get_all_clusters(iterable=True):
#   print(cluster['name'])
#
## Get A cluster
# print('===========Get A Cluster==========')
#
# out = a.Clusters.get_a_single_cluster('rsTest33')
# pprint(out)
#



#print('=========Create A Basic Cluster=====================')

#myoutput = a.Clusters.create_basic_rs(name=TEST_CLUSTER_NAME, disk_size=11,version=mdb_version.v4_2)

#test_cluster_name=myoutput.config.name



#pprint(myoutput.__dict__)


#print('=========Create A Cluster=====================')

#provider_settings: ProviderSettings = ProviderSettings()
#regions_config = RegionConfig()
#replication_specs = ReplicationSpecs(regions_config={provider_settings.region_name: regions_config.__dict__})
#
#cluster_config = ClusterConfig(name='test2',
#                               providerSettings=provider_settings,
#                               replication_specs=replication_specs)

#output = a.Clusters.create_a_cluster(cluster_config)
#
#pprint(output)


#print('===========Get A Cluster as data==========')

#out = a.Clusters.get_a_single_cluster_as_obj(cluster=TEST_CLUSTER_NAME)
#pprint('---Cluster Created----------')
#pprint(out.as_dict())


print('==========Modify a Cluster=================')

out = a.Clusters.get_a_single_cluster_as_obj(cluster=TEST_CLUSTER_NAME)
print('Retrieved information regarding cluster {}'.format(TEST_CLUSTER_NAME))
pprint('output is of type: {}'.format(type(out)))

print('===========Delete A Cluster==========')

# pprint(a.Clusters.is_existing_cluster(TEST_CLUSTER_NAME))

# a.Clusters.delete_a_cluster('QuickTest',True)

# out = create_basic_rs("test20")

# print(dumps(out.as_create_dict()))