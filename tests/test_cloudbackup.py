"""
Unit tests for Cloud Backup


"""
import datetime
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.cloud_backup import CloudBackupSnapshot, DeliveryType, SnapshotRestoreResponse
from atlasapi.clusters import ClusterStates, MongoDBMajorVersion, InstanceSizeName
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
        self.assertGreaterEqual(count, 1)
        print(f'✅The number of cloudbackup snapshots returned = {count} is greater than one.')

    test_00_test_get_for_cluster.basic = True

    def test_00a_test_get_for_cluster_no_snapshots(self):
        cluster_name = 'TestShared'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)
        count = 0
        for each in snapshots:
            count += 1
            self.assertEquals(type(each), CloudBackupSnapshot)
        self.assertEquals(count, 0, f"There should be no backups found for {cluster_name}")
        print(f'✅The number of cloudbackup snapshots returned for {cluster_name} equal to zero as expected.')

    test_00a_test_get_for_cluster_no_snapshots.basic = True

    def test_01_test_get_for_snapshot(self):
        cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)
        for each in snapshots:
            snapshot_id = each.id
            break

        print(f'The tested snapshot_id is {snapshot_id}')
        snapshot = self.a.CloudBackups.get_backup_snapshot_for_cluster(cluster_name=cluster_name,
                                                                       snapshot_id=snapshot_id)
        self.assertEquals(type(snapshot), CloudBackupSnapshot)

    test_01_test_get_for_snapshot.basic = True

    def test_02_create_snapshot(self):
        cluster_name = 'pyAtlasTestCluster'
        response_obj = self.a.CloudBackups.create_snapshot_for_cluster(cluster_name=cluster_name,
                                                                       retention_days=1,
                                                                       description=f"PyAtlasTest -"
                                                                                   f" {datetime.datetime.utcnow()}",
                                                                       )
        self.assertEquals(type(response_obj), CloudBackupSnapshot)
        print(f'New Snapshot created!! ({CloudBackupSnapshot})')

    test_02_create_snapshot.basic = False
    test_02_create_snapshot.advanced = True

    def test_03_restore_snapshot_to_atlas(self):
        source_cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=source_cluster_name)
        snapshot_id = None
        for each in snapshots:
            snapshot_id = each.id
            break
        print(f"✅Will restore snapshot id {snapshot_id}")
        # Create the restore-to cluster and wait.
        # first make sure the destination cluster has correct MDB version and disk size
        source_cluster_obj = self.a.Clusters.get_single_cluster(source_cluster_name)
        source_version = source_cluster_obj.mongodb_version.split(".")
        source_major_version = MongoDBMajorVersion(source_version[0] + '.' + source_version[1])
        print(f"The source version is: {source_major_version}")
        source_disk_size = source_cluster_obj.disk_size_gb
        print(f"🤹🏾‍Will create a desstination cluster: {self.TEST_CLUSTER2_NAME_UNIQUE}. version: {source_version}."
              f" Disk size: {source_disk_size}")
        _destination_cluster_obj = self.a.Clusters.create_basic_rs(name=self.TEST_CLUSTER2_NAME_UNIQUE,
                                                                   version=source_major_version,
                                                                   size=InstanceSizeName.M10,
                                                                   disk_size=source_disk_size)
        self.wait_for_cluster_state(self.TEST_CLUSTER2_NAME_UNIQUE, states_desired=[ClusterStates.IDLE],
                                    states_to_wait=[ClusterStates.REPAIRING, ClusterStates.CREATING,
                                                    ClusterStates.UPDATING, ClusterStates.DELETING])

        response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                    snapshot_id=snapshot_id,
                                                                    target_cluster_name=self.TEST_CLUSTER2_NAME_UNIQUE,
                                                                    delivery_type=DeliveryType.automated)
        # pprint(response_obj.__dict__)
        self.assertEquals(type(response_obj), SnapshotRestoreResponse)

    test_03_restore_snapshot_to_atlas.basic = False
    test_03_restore_snapshot_to_atlas.advanced = True

    def test_04_restore_snapshot_to_atlas_bad_snapshot_id(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'pyAtlasTestRestore'
        snapshot_id = '6104a8c6c1b4ef7788b5d8f0-322'
        with self.assertRaises(ValueError) as ex:
            response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                        snapshot_id=snapshot_id,
                                                                        target_cluster_name=target_cluster_name,
                                                                        delivery_type=DeliveryType.automated)
            pprint(response_obj)

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
            _response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
                                                                         snapshot_id=snapshot_id,
                                                                         target_cluster_name=target_cluster_name,
                                                                         delivery_type=DeliveryType.automated)

    test_06_restore_snapshot_to_atlas_bad_same_cluster.basic = True

    def test_07_get_restore_job_for_cluster(self):
        cluster_name = 'pyAtlasTestCluster'
        restores: List[SnapshotRestoreResponse] = self.a.CloudBackups.get_snapshot_restore_requests(
            cluster_name=cluster_name)
        count = 0
        for each in restores:
            count += 1
            # pprint(each.__dict__)

            self.assertEquals(type(each), SnapshotRestoreResponse)
        print(f'The number of snapshots restore jobs returned = {count}')
        self.assertGreaterEqual(count, 1)

    test_07_get_restore_job_for_cluster.basic = True

    def test_08_get_one_restore_job(self):
        cluster_name = 'pyAtlasTestCluster'
        restores: List[SnapshotRestoreResponse] = self.a.CloudBackups.get_snapshot_restore_requests(
           cluster_name=cluster_name)
        count = 0
        restore_id = list(restores)[0].restore_id

        print(f'The restore_id to be tested is {restore_id}')
        restore_id = '6316aa307a72486c7af60311'
        restore_jobs = self.a.CloudBackups.get_snapshot_restore_requests(cluster_name=cluster_name,
                                                                        restore_id=restore_id)

        restore_job = list(restore_jobs)[0]

        self.assertEquals(type(restore_job), SnapshotRestoreResponse)

    test_08_get_one_restore_job.basic = False

    def test_09_is_valid_snapshot_false(self):
        cluster_name = 'pyAtlasTestCluster'
        response = self.a.CloudBackups.is_existing_snapshot(cluster_name=cluster_name, snapshot_id='sdasdasd')
        self.assertEquals(response, False)

    test_09_is_valid_snapshot_false.basic = True

    def test_10_is_valid_snapshot_true(self):
        cluster_name = 'pyAtlasTestCluster'
        snapshots: List[CloudBackupSnapshot] = self.a.CloudBackups.get_backup_snapshots_for_cluster(
            cluster_name=cluster_name)

        snapshot_id = list(snapshots)[0].id
        print(f'The tested snapshot_id is {snapshot_id}')
        response = self.a.CloudBackups.is_existing_snapshot(cluster_name=cluster_name, snapshot_id=snapshot_id)

        self.assertEquals(response, True)

    test_10_is_valid_snapshot_true.basic = True

    def test_11_restore_snapshot_to_atlas_other_proj(self):
        source_cluster_name = 'pyAtlasTestCluster'
        target_cluster_name = 'pyAtlasTestRestore'
        snapshot_id = '6237a59f0942760c753d6df9'

        pprint(self.a_other.group)
        response_obj = self.a.CloudBackups.request_snapshot_restore_to_group(source_cluster_name=source_cluster_name,
                                                                             snapshot_id=snapshot_id,
                                                                             target_cluster_name=target_cluster_name,
                                                                             target_group_obj=self.a_other,
                                                                             delivery_type=DeliveryType.automated)
        self.assertEquals(type(response_obj), SnapshotRestoreResponse)

    test_11_restore_snapshot_to_atlas_other_proj.basic = False

#    def test_12_cancel_valid_restore_job(self):
#        source_cluster_name = 'pyAtlasTestCluster'
#        target_cluster_name = 'pyAtlasTestRestore'
#        snapshot_id = '619d5e979977cf1a6a9adfbf'
#        response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
#                                                                    snapshot_id=snapshot_id,
#                                                                    target_cluster_name=target_cluster_name,
#                                                                    delivery_type=DeliveryType.automated)
#
#        print(f"The restore_id of this test restore is {response_obj.restore_id}")
#        print(f"The canceled status is ({response_obj.cancelled})")
#        print(f"The completed date is {response_obj.finished_at}")
#
#        print("Now lets cancel this puppy")
#        out = self.a.CloudBackups.cancel_snapshot_restore_request(cluster_name=source_cluster_name,
#                                                                  restore_id=response_obj.restore_id)
#        pprint(f"({out})")
#
#    test_12_cancel_valid_restore_job.basic = True

#   def test_12a_cancel_valid_restore_job(self):
#     source_cluster_name = 'pyAtlasTestCluster'
#     target_cluster_name = 'pyAtlasTestRestore'
#     snapshot_id = '619d5e979977cf1a6a9adfbf'
#     response_obj = self.a.CloudBackups.request_snapshot_restore(source_cluster_name=source_cluster_name,
#                                                                 snapshot_id=snapshot_id,
#                                                                 target_cluster_name=target_cluster_name,
#                                                                 delivery_type=DeliveryType.automated)
#
#     print(f"The restore_id of this test restore is {response_obj.restore_id}")
#     print(f"The canceled status is ({response_obj.cancelled})")
#     print(f"The completed date is {response_obj.finished_at}")
#
#     print("Now lets cancel this puppy")
#     out = self.a.CloudBackups.cancel_snapshot_restore_request(cluster_name=source_cluster_name,
#                                                               restore_id="619d87217547a804f47a07e7")
#
#
#   test_12a_cancel_valid_restore_job.basic = True
