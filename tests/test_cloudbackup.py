"""
Unit tests for Maintenance Windows


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from cloud_backup import CloudBackupSnapshot, DeliveryType, SnapshotRestoreResponse
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
            # pprint(each)

            self.assertEquals(type(each), CloudBackupSnapshot)
        print(f'The number of cloudbackup snapshots returned = {count}')
        self.assertGreaterEqual(count,1)

    test_00_test_get_for_cluster.basic = True

    def test_01_test_get_for_snapshot(self):
        cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)

        snapshot_id =list(snapshots)[0].id
        print(f'The tested snapshot_id is {snapshot_id}')
        snapshot = self.a.CloudBackups.get_backup_snapshots_for_cluster(cluster_name=cluster_name,snapshot_id=snapshot_id)
        count = 0
        for each in snapshot:
            # pprint(each)
            self.assertEquals(type(each), CloudBackupSnapshot)

    test_01_test_get_for_snapshot.basic = True
    def test_02_create_snapshot(self):
        cluster_name = 'pyAtlasTestCluster'
        response_obj = self.a.CloudBackups.create_snapshot_for_cluster(cluster_name=cluster_name,
                                                                       retention_days=1,description="Test 01",as_obj=True)
        self.assertEquals(type(response_obj), CloudBackupSnapshot)
        pprint('New Snapshot created!!')
        # pprint(response_obj)

    test_02_create_snapshot.basic = False

    def test_03_restore_snapshot_to_atlas(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'restoreTest'
        snapshot_id = '6104a8c6c1b4ef7788b5d8f0'
        response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                    snapshot_id=snapshot_id,
                                                                    target_cluster_name=target_cluster_name,
                                                                    delivery_type=DeliveryType.automated)
        #pprint(response_obj.__dict__)
        self.assertEquals(type(response_obj),SnapshotRestoreResponse)

    test_03_restore_snapshot_to_atlas.basic = False

    def test_04_restore_snapshot_to_atlas_bad_snapshot_id(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'restoreTest'
        snapshot_id = '6104a8c6c1b4ef7788b5d8f0-322'
        with self.assertRaises(IOError) as ex:
            response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                    snapshot_id=snapshot_id,
                                                                    target_cluster_name=target_cluster_name,
                                                                    delivery_type=DeliveryType.automated)

    test_04_restore_snapshot_to_atlas_bad_snapshot_id.basic = True

    def test_05_restore_snapshot_to_atlas_bad_dest_cluster(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'restoreTest-222'
        snapshot_id = '6104a8c6c1b4ef7788b5d8f0'
        with self.assertRaises(ValueError) as ex:
            response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                    snapshot_id=snapshot_id,
                                                                    target_cluster_name=target_cluster_name,
                                                                    delivery_type=DeliveryType.automated)

    test_05_restore_snapshot_to_atlas_bad_dest_cluster.basic = True

    def test_06_restore_snapshot_to_atlas_bad_same_cluster(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'pyAtlasTestCluster'
        snapshot_id = '6104a8c6c1b4ef7788b5d8f0'
        with self.assertRaises(ValueError) as ex:
            response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                    snapshot_id=snapshot_id,
                                                                    target_cluster_name=target_cluster_name,
                                                                    delivery_type=DeliveryType.automated)

    test_06_restore_snapshot_to_atlas_bad_same_cluster.basic = True
