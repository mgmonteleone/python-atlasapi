"""
Unit tests for teting the network stack


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
from atlasapi.clusters import RegionConfig, AdvancedOptions, TLSProtocols, ClusterStates
from atlasapi.errors import ErrAtlasBadRequest

from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger('test')


class NetworkTests(BaseTests):

    def test_00_handle_400s(self):
        """
        Force a 400 error so we can test details being passed through.
        """
        try:
            cluster = self.a.Clusters.get_single_cluster(cluster=self.TEST_CLUSTER_NAME)
            update = self.a.Clusters.modify_cluster(cluster=self.TEST_CLUSTER_NAME,
                                                    cluster_config=dict(backupEnabled="whatevs"))
        except Exception as e:
            self.assertIsInstance(e, ErrAtlasBadRequest)
            error_code = e.getAtlasResponse()[0]
            self.assertEqual(error_code, 400, "The error code needs to be 400")
            print(f"Error Code is {error_code}")

    test_00_handle_400s.basic = True
