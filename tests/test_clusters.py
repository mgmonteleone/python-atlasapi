"""
Nose2 Unit Tests for the clusters module.


"""
from pprint import pprint
from os import environ, getenv

import atlasapi.errors
from atlasapi.atlas import Atlas
from atlasapi.lib import AtlasPeriods, AtlasUnits, AtlasGranularities
from json import dumps
from atlasapi.clusters import AtlasBasicReplicaSet, ClusterConfig
from atlasapi.lib import MongoDBMajorVersion as mdb_version, DefaultReadConcerns
from atlasapi.clusters import ClusterConfig, ProviderSettings, ReplicationSpecs, InstanceSizeName
from atlasapi.clusters import RegionConfig, AdvancedOptions, TLSProtocols
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ClusterTests(BaseTests):

    def test_00_get_all_clusters(self):
        cluster_list = self.a.Clusters.get_all_clusters()
        for each in cluster_list:
            print(
                f"✅ Found a {each.providerSettings.instance_size_name.value} cluster of type {each.cluster_type.value}✅")
            self.assertIsInstance(each, ClusterConfig)

    test_00_get_all_clusters.basic = True

    def test_03_get_a_cluster(self):
        cluster = self.a.Clusters.get_single_cluster(self.TEST_CLUSTER_NAME)
        print(f"✅ The cluster is of type {cluster.cluster_type.value}")
        self.assertIsInstance(cluster, ClusterConfig)
        print(f"✅ The cluster name is {cluster.name}")
        self.assertEqual(cluster.name, self.TEST_CLUSTER_NAME)
        # TODO: Add more data validation checks here, since we have a fixed configuration of the test cluster.

    test_03_get_a_cluster.basic = True

    def test_04_create_basic_cluster(self):
        myoutput = self.a.Clusters.create_basic_rs(name=self.TEST_CLUSTER2_NAME_UNIQUE, version=mdb_version.v4_2,
                                                   size=InstanceSizeName.M10)
        self.assertEqual(type(myoutput), AtlasBasicReplicaSet)
        pprint(myoutput.config.as_dict)
        print('-------------------Waiting a bit to allow the cluster to be created......-------------')
        sleep(30)
        print('-----------------------------------Done Sleeping -------------------------------------')

    test_04_create_basic_cluster.advanced = True

    def test_05_modify_cluster_disk(self):
        existing = self.a.Clusters.get_single_cluster_as_obj(cluster=self.TEST_CLUSTER_NAME)
        old_size = existing.disk_size_gb
        new_size = existing.disk_size_gb + 1
        existing.disk_size_gb = new_size
        new_config = self.a.Clusters.modify_cluster(self.TEST_CLUSTER_NAME, existing)
        pprint('Old Size: {}.  New Size {}'.format(old_size, new_size))
        self.assertEquals(new_config.get('diskSizeGB', 0), new_size), new_config
        print('-------------------Waiting a bit to allow the cluster to be modified......-------------')
        sleep(20)
        print('-----------------------------------Done Sleeping -------------------------------------')

    def test_06_delete_cluster(self):
        myoutput = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER2_NAME_UNIQUE, areYouSure=True)
        print('Successfully Deleted {}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, myoutput))

    test_06_delete_cluster.advanced = True

    def test_07_create_cluster(self):
        provider_settings: ProviderSettings = ProviderSettings()
        regions_config = RegionConfig()
        replication_specs = ReplicationSpecs(regions_config={provider_settings.region_name: regions_config.__dict__})
        cluster_config = ClusterConfig(name=self.TEST_CLUSTER3_NAME_UNIQUE,
                                       providerSettings=provider_settings,
                                       replication_specs=replication_specs)

        output = self.a.Clusters.create_cluster(cluster_config)
        pprint(output)

    test_07_create_cluster.advanced = True

    def test_08_resize_a_cluster(self):
        self.a.Clusters.modify_cluster_instance_size(cluster=self.TEST_CLUSTER3_NAME_UNIQUE,
                                                     new_cluster_size=InstanceSizeName.M20)

    test_08_resize_a_cluster.advanced = True

    def test_09_deleted_resized_cluster(self):
        output = self.a.Clusters.delete_cluster(cluster=self.TEST_CLUSTER3_NAME_UNIQUE, areYouSure=True)
        print('Successfully Deleted resized cluster :{}, output was '.format(self.TEST_CLUSTER2_NAME_UNIQUE, output))

    test_09_deleted_resized_cluster.advanced = True

    def test_10_pause_cluster(self):
        pprint('Pausing Cluster {}'.format(self.TEST_CLUSTER_NAME))
        try:
            out = self.a.Clusters.pause_cluster(cluster=self.TEST_CLUSTER_NAME, toggle_if_paused=True)
            self.assertTrue(type(out), dict), "Out Type is {}".format(type(out))
        except Exception as e:
            if e.details.get('errorCode') == 'CANNOT_PAUSE_RECENTLY_RESUMED_CLUSTER':
                print("We are working to fast. {}".format(e.details.get('detail')))
                pass

    test_10_pause_cluster.advanced = True

    def test_11_test_failover(self):
        try:
            self.a.Clusters.test_failover(self.TEST_CLUSTER_NAME)
        except atlasapi.errors.ErrAtlasBadRequest as e:
            if e.code == 'CLUSTER_RESTART_IN_PROGRESS':
                self.assertTrue(True)
                logger.warning('A cluster retstart was already in effect, so passing this test.')

    test_11_test_failover.basic = False

    def test_12_get_advanced_options(self):
        out_obj = self.a.Clusters.get_single_cluster_advanced_options(self.TEST_CLUSTER_NAME)
        print(f'✅ received a {type(out_obj)} object, which looks like this {str(out_obj.__dict__)[0:80]} . . .')
        self.assertEqual(type(out_obj), AdvancedOptions, msg='Output should be and AdvancedOptions object')

    test_12_get_advanced_options.basic = True

    def test_13_set_advanced_options(self):
        # Removed this test, since it is now failing due to this option no longer supported in 4.2 +.
        # Will need to remove the
        # set_1 = AdvancedOptions(failIndexKeyTooLong=True)
        # out_set_1 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
        #                                                            advanced_options=set_1)

        set_2 = AdvancedOptions(javascriptEnabled=True)

        out_set_2 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                                    advanced_options=set_2)
        self.assertEqual(set_2.javascriptEnabled, out_set_2.javascriptEnabled,
                         msg='in = {}: out= {}'.format(set_2.__dict__, out_set_2.__dict__))
        print(f"✅ Checked javascriptEnabled = {set_2.javascriptEnabled} ")

        set_3 = AdvancedOptions(minimumEnabledTlsProtocol=TLSProtocols.TLS1_2)
        out_set_3 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                                    advanced_options=set_3)
        self.assertEqual(set_3.minimumEnabledTlsProtocol, out_set_3.minimumEnabledTlsProtocol,
                         msg='in = {}: out= {}'.format(set_3.__dict__, out_set_3.__dict__))

        print(f"✅ Checked minimumEnabledTlsProtocol = {set_3.minimumEnabledTlsProtocol} ")

        set_4 = AdvancedOptions(noTableScan=True)
        out_set_4 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                                    advanced_options=set_4)
        self.assertEqual(set_4.noTableScan, out_set_4.noTableScan,
                         msg='in = {}: out= {}'.format(set_4.__dict__, out_set_4.__dict__))
        print(f"✅ Checked noTableScan = {set_4.noTableScan} ")
        set_4_revert = AdvancedOptions(noTableScan=False)
        print(f"↩️ Reverting noTableScan = {set_4_revert.noTableScan} ")
        self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                        advanced_options=set_4_revert)

        set_5 = AdvancedOptions(oplogSizeMB=1000)
        out_set_5 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                                    advanced_options=set_5)
        self.assertEqual(set_5.oplogSizeMB, out_set_5.oplogSizeMB,
                         msg='in = {}: out= {}'.format(set_5.__dict__, out_set_5.__dict__))
        print(f"✅ Checked oplogSizeMB = {set_5.oplogSizeMB} ")

        set_6 = AdvancedOptions(defaultReadConcern=DefaultReadConcerns.local)
        out_set_6 = self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                                    advanced_options=set_6)
        self.assertEqual(set_6.defaultReadConcern, out_set_6.defaultReadConcern,
                         msg='in = {}: out= {}'.format(set_6.__dict__, out_set_6.__dict__))
        print(f"✅ Checked defaultReadConcern = {set_6.defaultReadConcern} ")
        set_6_revert = AdvancedOptions(defaultReadConcern=DefaultReadConcerns.available)
        print(f"↩️ Reverting defaultReadConcern = {set_6_revert.defaultReadConcern} ")
        self.a.Clusters.modify_cluster_advanced_options(cluster=self.TEST_CLUSTER_NAME,
                                                        advanced_options=set_6_revert)

    test_13_set_advanced_options.basic = True

    def test_14_set_tls(self):
        new_TLS = TLSProtocols.TLS1_0
        returned_val = self.a.Clusters.modify_cluster_tls(cluster=self.TEST_CLUSTER_NAME, TLS_protocol=new_TLS)
        self.assertEqual(new_TLS, returned_val)
        print(f"✅ Checked that TLS value matches {returned_val.name}")
        revert_TLS = TLSProtocols.TLS1_2
        returned_val = self.a.Clusters.modify_cluster_tls(cluster=self.TEST_CLUSTER_NAME, TLS_protocol=revert_TLS)
        self.assertEqual(revert_TLS, returned_val)
        print(f"✅ Checked that TLS value matches {returned_val.name}")
