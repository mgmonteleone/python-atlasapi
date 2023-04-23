"""
Unit tests for getting measurements and hosts


"""
from pprint import pprint
from os import environ, getenv

import atlasapi.specs
import atlasapi.measurements
from atlasapi.atlas import Atlas
from json import dumps
from tests import BaseTests
import logging
from time import sleep
from atlasapi.lib import AtlasUnits, ClusterType
from atlasapi.specs import Host, AtlasPeriods, AtlasGranularities, ReplicaSetTypes
from atlasapi.measurements import AtlasMeasurementTypes, AtlasMeasurementValue, AtlasMeasurement
from atlasapi import events_event_types
from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger('test')


# noinspection PyTypeChecker
class MeasurementTests(BaseTests):

    def test_00_check_event_types(self):

        my_events = events_event_types

        test = my_events.AtlasEventTypes.TEST_FAILOVER_REQUESTED
        print(test)

    test_00_check_event_types.basic = True
    def test_00_get_hosts_count(self):
        atlas: Atlas = self.a
        atlas.Hosts.fill_host_list()
        self.assertGreater(len(atlas.Hosts.host_list), 2)

    test_00_get_hosts_count.basic = True

    def test_01_get_cluster_names(self):
        self.a.Hosts.fill_host_list()
        cluster_list = self.a.Hosts.cluster_list

        # for each_cluster in cluster_list:
        #    pprint(each_cluster)
        self.assertGreater(len(cluster_list), 0)

    test_01_get_cluster_names.basic = True

    def test_02_fill_measurement(self):
        self.a.Hosts.fill_host_list()
        self.assertGreaterEqual(len(self.a.Hosts.host_list), 2)
        self.a.Hosts.get_measurement_for_hosts(measurement=AtlasMeasurementTypes.connections)
        for each in self.a.Hosts.host_list_with_measurements:
            self.assertIsInstance(each, Host)
            self.assertGreaterEqual(len(each.measurements), 1)
            for each_measurement in each.measurements:
                print(
                    f'The Mean values are: {each.hostname}: {each_measurement.name}: '
                    f'{each_measurement.measurement_stats.mean}')
                print(f'The Mean values are: {each.hostname}: {each_measurement.name}:'
                      f' {each_measurement.measurement_stats.mean}')
                self.assertIsInstance(each_measurement, AtlasMeasurement)

    test_02_fill_measurement.basic = True

    def test_03_measurement_stats(self):
        self.a.Hosts.fill_host_list()
        self.a.Hosts.get_measurement_for_hosts()
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_03_measurement_stats.basic = True

    def test_04_measurement_stats_objects(self):
        measurement = AtlasMeasurementTypes.QueryTargetingScanned.objects_per_returned,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_04_measurement_stats_objects.basic = True

    def test_05_measurement_stats_objects_returned(self):
        measurement = AtlasMeasurementTypes.QueryTargetingScanned.per_returned,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_05_measurement_stats_objects_returned.basic = True

    def test_06_measurement_stats_cache_bytes_into(self):
        measurement = AtlasMeasurementTypes.Cache.bytes_read,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'👍Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_06_measurement_stats_cache_bytes_into.basic = True

    def test_07_measurement_stats_cache_bytes_from(self):
        measurement = AtlasMeasurementTypes.Cache.bytes_written,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'👍Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_07_measurement_stats_cache_bytes_from.basic = True

    def test_08_measurement_stats_cache_dirty(self):
        measurement = AtlasMeasurementTypes.Cache.dirty,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'👍Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_08_measurement_stats_cache_dirty.basic = True

    def test_09_measurement_stats_cache_used(self):
        measurement = AtlasMeasurementTypes.Cache.used,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)
            print(f'👍Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_09_measurement_stats_cache_used.basic = True

    def test_10_measurement_stats_tickets(self):
        measurements = [AtlasMeasurementTypes.TicketsAvailable.reads, AtlasMeasurementTypes.TicketsAvailable.writes]
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        for measurement in measurements:
            self.a.Hosts.fill_host_list()
            self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
            print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
            for each in self.a.Hosts.host_list_with_measurements[0].measurements:
                print(f'For metric {each.name}')
                print(f'👍Value is {each.measurement_stats_friendly}')
                self.assertIsInstance(each.measurement_stats_friendly, atlasapi.measurements.StatisticalValuesFriendly)

    test_10_measurement_stats_tickets.basic = True

    def test_11_measurement_stats_connections(self):
        measurements = [AtlasMeasurementTypes.connections]
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        for measurement in measurements:
            self.a.Hosts.fill_host_list()
            self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
            print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
            for each in self.a.Hosts.host_list_with_measurements[0].measurements:
                logger.info(f'For metric {each.name}'.center(80, '*'))
                logger.info(f'👍Value is {each.measurement_stats}'.center(80, '*'))
                self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    test_11_measurement_stats_connections.basic = True

    def test_12_issue_90_get_measurement_for_host(self):
        self.a.Hosts.fill_host_list()
        for each_host in self.a.Hosts.host_list:
            measurements = list(
                each_host.get_measurement_for_host(atlas_obj=self.a, measurement=AtlasMeasurementTypes.connections))
            each_host.add_measurements(measurements)
            self.assertIsInstance(each_host.measurements[0], AtlasMeasurement)
            pprint(each_host.measurements[0].measurement_stats.mean)

    test_12_issue_90_get_measurement_for_host.basic = True

    def test_13_get_multiple_metrics_at_once_for_host(self):
        self.a.Hosts.fill_host_list()
        test_host: Host = self.a.Hosts.host_list[0]
        measurements = test_host.get_measurement_for_host(atlas_obj=self.a, measurement=AtlasMeasurementTypes.Cache)
        for each in measurements:
            self.assertIsInstance(each, AtlasMeasurement)
            for each_one in each.measurements:
                self.assertIsInstance(each_one, AtlasMeasurementValue)

    test_13_get_multiple_metrics_at_once_for_host.basic = True

    def test_14_return_primaries(self):
        self.a.Hosts.fill_host_list()
        for each_host in self.a.Hosts.host_list_primaries:
            print(f'Cluster: {each_host.cluster_name}, Host: {each_host.hostname}, is type: {each_host.type}')
            self.assertEqual(each_host.type, ReplicaSetTypes.REPLICA_PRIMARY)

    test_14_return_primaries.basic = True

    def test_15_return_secondaries(self):
        self.a.Hosts.fill_host_list()
        for each_host in self.a.Hosts.host_list_secondaries:
            print(f'Cluster: {each_host.cluster_name}, Host: {each_host.hostname}, is type: {each_host.type}')
            self.assertEqual(each_host.type, ReplicaSetTypes.REPLICA_SECONDARY)

    test_15_return_secondaries.basic = True

    def test_16_issue_98_metric_name_write(self):
        measurements = [AtlasMeasurementTypes.TicketsAvailable.writes]
        granularity = AtlasGranularities.DAY,
        period = AtlasPeriods.WEEKS_1
        for measurement in measurements:
            self.a.Hosts.fill_host_list()
            self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
            print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
            for each in self.a.Hosts.host_list_with_measurements[0].measurements:
                print(f'For metric {each.name}')
                print(f'👍Value is {each.measurement_stats_friendly.__dict__}')
                self.assertIsInstance(each.measurement_stats, atlasapi.measurements.StatisticalValues)

    def test_17_return_multiple_metrics(self):
        self.a.Hosts.fill_host_list()
        for each_host in self.a.Hosts.host_list_secondaries:
            print(
                f'Cluster: {each_host.cluster_name}, Host: {each_host.hostname}, is type'
                f': {each_host.type} ia port {each_host.port}')
            self.assertEqual(each_host.type, ReplicaSetTypes.REPLICA_SECONDARY)
            measurements = list(
                each_host.get_measurement_for_host(atlas_obj=self.a, measurement=AtlasMeasurementTypes.Db.data_size))
            each_host.add_measurements(measurements)
            for each_measurement in each_host.measurements:
                print(each_measurement.measurement_stats.mean)

    def test_18_return_no_hosts_if_wrong_filter(self):
        self.a.Hosts.fill_host_list(for_cluster='monkeypants')
        self.assertEqual(len(list(self.a.Hosts.host_list)), 0)

    test_18_return_no_hosts_if_wrong_filter.basic = True

    def test_19_issue101_case_insensitive_clustername(self):
        self.a.Hosts.fill_host_list(for_cluster='pyAtlasTestCluster')
        self.assertGreater(len(list(self.a.Hosts.host_list)), 1)

    test_19_issue101_case_insensitive_clustername.basic = True

    def test_20_issue_104_hyphen_in_cluster_name(self):
        cluster_name = 'cluster-02'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        for each in self.a.Hosts.host_list:
            print(
                f'cluster: {each.cluster_name} - Host: {each.hostname_alias}'
                f' cluster_name_alias= {each.cluster_name_alias}')
            self.assertEqual(cluster_name, each.cluster_name_alias)

    test_20_issue_104_hyphen_in_cluster_name.basic = False

    def test_21_get_partitions_for_host(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)

        for each_host in self.a.Hosts.host_list:
            partition_names = each_host.get_partitions(self.a)
            for each_partition in partition_names:
                self.assertIsInstance(each_partition, str, f"This should return a partition name as str, instead it "
                                                           f"returned {type(each_partition)}")

    test_21_get_partitions_for_host.basic = True

    def test_22_get_measurements_for_partition(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        for each_host in self.a.Hosts.host_list:
            pprint(f"For Host: {each_host.hostname}")
            partition_names = each_host.get_partitions(self.a)
            for each_partition in partition_names:
                output: AtlasMeasurement = each_host.get_measurements_for_disk(self.a, each_partition)
                for each in output:
                    print('Measurement'.center(80, '*'))
                    print(f"Name: {each.name}: {each.measurement_stats_friendly.mean} {each.units}")
                    self.assertIsInstance(each.measurement_stats_friendly,
                                          atlasapi.measurements.StatisticalValuesFriendly)

    test_22_get_measurements_for_partition.basic = True

    def test_23_get_measurements_for_data_partition(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        for each_host in self.a.Hosts.host_list:
            pprint(f"For Host: {each_host.hostname}")
            output: AtlasMeasurement = each_host.data_partition_stats(self.a)
            for each in output:
                print('Measurement'.center(80, '*'))
                print(f"Name: {each.name}: {each.measurement_stats_friendly.mean} {each.units}")
                self.assertIsInstance(each.measurement_stats_friendly,
                                      atlasapi.measurements.StatisticalValuesFriendly)

    test_23_get_measurements_for_data_partition.basic = True

    def test_24_get_databases(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        for each_host in self.a.Hosts.host_list:
            output = each_host.get_databases(self.a)
            db_list = []
            for each_db in output:
                db_list.append(each_db)
            print(f'There are are {len(db_list)} dbs on {each_host.hostname_alias}'.center(120, '*'))
            self.assertGreaterEqual(len(db_list), 2, "There should be at least two datbases on each host!")

    test_24_get_databases.basic = True

    def test_25_get_measurements_for_configdb(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        for each_host in self.a.Hosts.host_list:
            pprint(f"For Host: {each_host.hostname}")
            output: AtlasMeasurement = each_host.get_measurements_for_database(self.a, database_name="sample_airbnb")
            for each in output:
                print('Measurement'.center(80, '*'))
                print(f"Name: {each.name}: {each.measurement_stats_friendly.mean} {each.units}")
                self.assertIsInstance(each.measurement_stats_friendly,
                                      atlasapi.measurements.StatisticalValuesFriendly)

    test_25_get_measurements_for_configdb.basic = True

    def test_26_issue_114_add_ten_second_granularity(self):
        cluster_name = 'pyAtlasTestCluster'
        self.a.Hosts.fill_host_list(for_cluster=cluster_name)
        host = list(self.a.Hosts.host_list)[0]
        pprint(f"For Host: {host.hostname}")
        output: AtlasMeasurement = host.get_measurements_for_disk(self.a, partition_name="data",
                                                                  granularity=AtlasGranularities.TEN_SECOND,
                                                                  period=AtlasPeriods.HOURS_24)
        for each in output:
            print('Measurement'.center(80, '*'))
            print(f"Name: {each.name}: {each.measurement_stats_friendly.mean} {each.units} {each.granularity}")

    # This test requires a cluster of m40 or higher , so will not run this in the automated suite.
    test_26_issue_114_add_ten_second_granularity.basic = False
