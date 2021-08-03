"""
Unit tests for Maintenance Windows


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from cloud_backup import CloudBackupSnapshot
from json import dumps
from tests import BaseTests
import logging
from time import sleep
from typing import List

logger = logging.getLogger('test')


class CloudBackupTests(BaseTests):

    def test_00_test_get_for_cluster(self):
        cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)
        count = 0
        for each in snapshots:
            count += 1
            pprint(each)

            self.assertEquals(type(each), CloudBackupSnapshot)
        print(f'The number of cloudbackup snapshots returned = {count}')
        self.assertGreaterEqual(count,1)

    test_00_test_get_for_cluster.basic = True

    def test_01_test_get_for_snapshot(self):
        cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)

        snapshot_id =list(snapshots)[0].id
        pprint(snapshot_id)
        snapshot = self.a.CloudBackups.get_backup_snapshots_for_cluster(cluster_name=cluster_name,snapshot_id=snapshot_id)
        count = 0
        for each in snapshot:
            pprint(each)
            self.assertEquals(type(each), CloudBackupSnapshot)


