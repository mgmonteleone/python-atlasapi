"""
Stupid and simple smoke tests.

Uses ENV vars to store user, key and group.

TODO: Create real tests


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from json import dumps
from atlasapi.clusters import AtlasBasicReplicaSet, MongoDBMajorVersion as mdb_version, ClusterConfig
from atlasapi.clusters import ClusterConfig, ProviderSettings, ReplicationSpecs, InstanceSizeName
from atlasapi.clusters import RegionConfig
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ClusterTests(BaseTests):

    def test_00_get_all_clusters(self):
        cluster_list = list(self.a.Clusters.get_all_clusters(iterable=True))

        self.assertTrue(type(cluster_list) is list)

    def test_01_get_all_clusters_type(self):
        cluster_list = list(self.a.Clusters.get_all_clusters(iterable=True))
        for each_cluster in cluster_list:
            logger.warning(each_cluster)
            self.assertTrue(type(each_cluster) is dict)

    def test_02_get_a_cluster_as_obj(self):
        cluster = self.a.Clusters.get_single_cluster_as_obj(self.TEST_CLUSTER_NAME)
        self.assertTrue(type(cluster) is ClusterConfig)
        self.assertEqual(cluster.name, self.TEST_CLUSTER_NAME)

    def test_03_get_a_cluster(self):
        cluster = self.a.Clusters.get_single_cluster(self.TEST_CLUSTER_NAME)
        self.assertTrue(type(cluster) is dict)
        self.assertEqual(cluster['name'], self.TEST_CLUSTER_NAME)

    def test_04_create_basic_cluster(self):
        myoutput = self.a.Clusters.create_basic_rs(name=self.TEST_CLUSTER2_NAME_UNIQUE, version=mdb_version.v4_2,
                                                   size=InstanceSizeName.M10)
        self.assertEqual(type(myoutput), AtlasBasicReplicaSet)
        pprint(myoutput.config.as_dict())
        pprint('-------------------Waiting a bit to allow the cluster to be created......-------------')
        sleep(30)
        pprint('-----------------------------------Done Sleeping -------------------------------------')

    def test_05_modify_cluster_disk(self):
        existing = self.a.Clusters.get_single_cluster_as_obj(cluster=self.TEST_CLUSTER2_NAME_UNIQUE)
        old_size = existing.disk_size_gb
        new_size = existing.disk_size_gb + 1
        existing.disk_size_gb = new_size
        new_config = self.a.Clusters.modify_cluster(self.TEST_CLUSTER2_NAME_UNIQUE, existing)
        pprint('Old Size: {}.  New Size {}'.format(old_size, new_size))
        self.assertEquals(new_config.get('diskSizeGB', 0), new_size), new_config
        pprint('-------------------Waiting a bit to allow the cluster to be modified......-------------')
        sleep(60)
        pprint('-----------------------------------Done Sleeping -------------------------------------')

    def test_06_delete_a_cluster(self):
        myoutput = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER2_NAME_UNIQUE, areYouSure=True)
        print('Successfully Deleted {}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, myoutput))

    def test_07_create_a_cluster(self):
        provider_settings: ProviderSettings = ProviderSettings()
        regions_config = RegionConfig()
        replication_specs = ReplicationSpecs(regions_config={provider_settings.region_name: regions_config.__dict__})
        cluster_config = ClusterConfig(name=self.TEST_CLUSTER3_NAME_UNIQUE,
                                       providerSettings=provider_settings,
                                       replication_specs=replication_specs)

        output = self.a.Clusters.create_cluster(cluster_config)
        pprint(output)

    def test_08_resize_a_cluster(self):
        output = self.a.Clusters.modify_cluster_instance_size(cluster=self.TEST_CLUSTER3_NAME_UNIQUE,
                                                              new_cluster_size=InstanceSizeName.M20)
        pprint(output)

    def test_09_deleted_resized_cluster(self):
        output = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER3_NAME_UNIQUE,areYouSure=True)
        print('Successfully Deleted resized cluster :{}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, output))


