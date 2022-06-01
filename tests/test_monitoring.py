"""
Unit tests for getting measurements and hosts


"""
from pprint import pprint
from os import environ, getenv

import atlasapi.specs
from atlasapi.atlas import Atlas
from json import dumps
from tests import BaseTests
import logging
from time import sleep
from atlasapi.lib import AtlasUnits, ClusterType
from atlasapi.specs import AtlasMeasurement, Host, AtlasPeriods, AtlasGranularities, AtlasMeasurementTypes
from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger('test')


class MeasurementTests(BaseTests):

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
        out = self.a.Hosts.get_measurement_for_hosts(return_data=True)
        self.assertGreaterEqual(len(self.a.Hosts.host_list_with_measurements), 3)
        for each in self.a.Hosts.host_list_with_measurements:
            self.assertIsInstance(each, Host)
            self.assertGreaterEqual(len(each.measurements), 1)
            for each_measurement in each.measurements:
                print(
                    f'The Mean values are: {each.hostname}: {each_measurement.name}: {each_measurement.measurement_stats.mean}')
                print(f'The Mean values are: {each.hostname}: {each_measurement.name}: {each_measurement.measurement_stats.mean}')
                self.assertIsInstance(each_measurement, AtlasMeasurement)

    test_02_fill_measurement.basic = True

    def test_03_measurement_stats(self):
        self.a.Hosts.fill_host_list()
        self.a.Hosts.get_measurement_for_hosts()
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_bytes, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_bytes.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

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
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_03_measurement_stats.basic = True

    def test_04_measurement_stats_objects(self):
        measurement = AtlasMeasurementTypes.QueryTargetingScanned.objects_per_returned,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_number, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_number.__dict__}')
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_04_measurement_stats_objects.basic = True

    def test_05_measurement_stats_cache_bytes_into(self):
        measurement = AtlasMeasurementTypes.Cache.bytes_read,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_bytes, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_bytes.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_05_measurement_stats_cache_bytes_into.basic = True

    def test_05_measurement_stats_cache_bytes_from(self):
        measurement = AtlasMeasurementTypes.Cache.bytes_written,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_bytes, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_bytes.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_05_measurement_stats_cache_bytes_into.basic = True

    def test_06_measurement_stats_cache_dirty(self):
        measurement = AtlasMeasurementTypes.Cache.dirty,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_bytes, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_bytes.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_06_measurement_stats_cache_dirty.basic = True

    def test_07_measurement_stats_cache_used(self):
        measurement = AtlasMeasurementTypes.Cache.used,
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        self.a.Hosts.fill_host_list()
        print(f'THe original data type sent for measurement is {type(measurement)}')
        self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
        print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
        for each in self.a.Hosts.host_list_with_measurements[0].measurements:
            print(f'For metric {each.name}')
            self.assertIsInstance(each.measurement_stats_friendly_bytes, atlasapi.specs.StatisticalValuesFriendly)
            print(f'Value is {each.measurement_stats_friendly_bytes.__dict__}')
            self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_07_measurement_stats_cache_used.basic = True

    def test_08_measurement_stats_tickets(self):
        measurements = [AtlasMeasurementTypes.TicketsAvailable.reads, AtlasMeasurementTypes.TicketsAvailable.writes]
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        for measurement in measurements:
            self.a.Hosts.fill_host_list()
            self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
            print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
            for each in self.a.Hosts.host_list_with_measurements[0].measurements:
                print(f'For metric {each.name}')
                self.assertIsInstance(each.measurement_stats_friendly_number, atlasapi.specs.StatisticalValuesFriendly)
                print(f'Value is {each.measurement_stats_friendly_number.__dict__}')
                self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_08_measurement_stats_tickets.basic = True

    def test_09_measurement_stats_connections(self):
        measurements = [AtlasMeasurementTypes.connections]
        granularity = AtlasGranularities.HOUR,
        period = AtlasPeriods.WEEKS_4
        for measurement in measurements:
            self.a.Hosts.fill_host_list()
            self.a.Hosts.get_measurement_for_hosts(measurement=measurement, granularity=granularity, period=period)
            print(f'For {self.a.Hosts.host_list_with_measurements.__len__()} hosts:')
            for each in self.a.Hosts.host_list_with_measurements[0].measurements:
                print(f'For metric {each.name}')
                self.assertIsInstance(each.measurement_stats_friendly_number, atlasapi.specs.StatisticalValuesFriendly)
                print(f'Value is {each.measurement_stats_friendly_number.__dict__}')
                self.assertIsInstance(each.measurement_stats, atlasapi.specs.StatisticalValues)

    test_09_measurement_stats_connections.basic = True

    test_04_measurement_stats_objects.basic = True
