import unittest
from os import getenv, environ

try:
    from atlasapi.atlas import Atlas
    from atlasapi.clusters import ClusterStates
except NameError:
    from atlas import Atlas
    from clusters import ClusterStates
from datetime import datetime
import coolname
from time import sleep, time
import humanfriendly

TEST_CLUSTER_NAME = getenv('TEST_CLUSTER_NAME', 'pyAtlasTestCluster')
TEST_CLUSTER2_NAME = getenv('TEST_CLUSTER2_NAME', 'pyAtlas-')

test_run_id = coolname.generate_slug(2)

TEST_CLUSTER_NAME_UNIQUE = TEST_CLUSTER_NAME + test_run_id
TEST_CLUSTER2_NAME_UNIQUE = TEST_CLUSTER2_NAME + test_run_id
TEST_CLUSTER3_NAME_UNIQUE = TEST_CLUSTER2_NAME + coolname.generate_slug(2)
CLUSTER_CREATE_WAIT_SECONDS = 60 * 10
TEST_SERVERLESS_NAME = f"serverless{test_run_id}"
ephemeral_test_clusters = [TEST_CLUSTER_NAME_UNIQUE, TEST_CLUSTER2_NAME_UNIQUE, TEST_CLUSTER3_NAME_UNIQUE]


class BaseTests(unittest.TestCase):
    def wait_for_cluster_state(self, cluster_name: str, states_desired: list = None, states_to_wait: list = None):
        if not states_to_wait:
            states_to_wait = [ClusterStates.CREATING, ClusterStates.UPDATING, ClusterStates.REPAIRING]
        if not states_desired:
            states_desired = [ClusterStates.IDLE]
        t_end = time() + self.CLUSTER_CREATE_WAIT_SECONDS
        seconds_elapsed = 0
        print(f"The states to wait for are: {states_to_wait}")
        print(f"The states desired are: {states_desired}")
        while time() < t_end:
            cluster_state = ClusterStates[self.a.Clusters.get_single_cluster(cluster=cluster_name).get('stateName')]
            print(f"⏲⏲ THe Cluster State is: {cluster_state}")
            if cluster_state in states_to_wait:
                print(
                    f"⏳The cluster {cluster_name} is still creating (state= {cluster_state.value}), "
                    f"will wait 15 seconds before polling again. {humanfriendly.format_timespan(seconds_elapsed)} "
                    f"elapsed of {humanfriendly.format_timespan(self.CLUSTER_CREATE_WAIT_SECONDS)}")
                seconds_elapsed += 15
                sleep(15)
            elif cluster_state in states_desired:
                print(f"✅The cluster {self.TEST_CLUSTER3_NAME_UNIQUE} is now in {cluster_state} state!! It took "
                      f"{humanfriendly.format_timespan(seconds_elapsed)}")
                break
        print(f"🔎🔎 The cluster {cluster_name} is in {self.a.Clusters.get_single_cluster(cluster=cluster_name)} state.")
        if ClusterStates[self.a.Clusters.get_single_cluster(cluster=cluster_name).get('stateName')] not in states_desired:
            msg = f"🙅🏽The cluster {cluster_name} did not get to {states_to_wait} state within the timeout of" \
                  f" {self.CLUSTER_CREATE_WAIT_SECONDS} 🆘 Makes sure you manually clean up the cluster if needed!!."
            print(msg)
            raise TimeoutError(msg)

    def setUp(self):
        self.USER = getenv('ATLAS_USER', None)
        self.API_KEY = getenv('ATLAS_KEY', None)
        self.GROUP_ID = getenv('ATLAS_GROUP', None)
        self.OTHER_GROUP_ID = getenv('ATLAS_OTHER_GROUP', None)
        self.OTHER_USER = getenv('ATLAS_OTHER_USER', None)
        self.OTHER_API_KEY = getenv('ATLAS_OTHER_KEY', None)

        # print("env var is".format(getenv('ATLAS_USER', None)))

        self.GROUP_OWNER_USER = getenv('ATLAS_ORG_USER', None)
        self.GROUP_OWNER_KEY = getenv('ATLAS_ORG_KEY', None)

        self.TEST_CLUSTER_NAME = TEST_CLUSTER_NAME
        self.TEST_CLUSTER2_NAME = TEST_CLUSTER2_NAME

        self.TEST_CLUSTER_NAME_UNIQUE = TEST_CLUSTER2_NAME_UNIQUE
        self.TEST_CLUSTER2_NAME_UNIQUE = TEST_CLUSTER2_NAME_UNIQUE
        self.TEST_CLUSTER3_NAME_UNIQUE = TEST_CLUSTER3_NAME_UNIQUE
        self.TEST_SERVERLESS_NAME = TEST_SERVERLESS_NAME

        if not self.USER or not self.API_KEY or not self.GROUP_ID:
            raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                                   'your env variables are {}'.format(environ.__str__()))
        self.a = Atlas(self.USER, self.API_KEY, self.GROUP_ID)
        self.a_other = Atlas(self.OTHER_USER, self.OTHER_API_KEY, self.OTHER_GROUP_ID)
        self.a_owner = Atlas(self.GROUP_OWNER_USER, self.GROUP_OWNER_KEY)

        self.CLUSTER_CREATE_WAIT_SECONDS = CLUSTER_CREATE_WAIT_SECONDS

        # make sure test cluster is unpaused
        print(f"🚀🚀🚀 Pre Test Checks........")
        try:
            print(f"🚀Making sure the {TEST_CLUSTER_NAME} is not paused. . .")
            self.wait_for_cluster_state(TEST_CLUSTER_NAME, states_desired=[ClusterStates.IDLE, ClusterStates.UPDATING],
                                        states_to_wait=[ClusterStates.CREATING, ClusterStates.REPAIRING, ClusterStates])
        except Exception as e:
            raise e

    # executed after each test

    def clean_up_cluster(self, cluster_name):
        if self.a.Clusters.is_existing_cluster(cluster_name):
            if self.a.Clusters.get_single_cluster(cluster_name).state_name not in \
                    [ClusterStates.DELETED, ClusterStates.DELETING]:
                print(f"🧹👀{cluster_name} found, and needs to be cleaned up.")
                self.a.Clusters.delete_cluster(cluster_name, areYouSure=True)
                self.wait_for_cluster_state(cluster_name, [ClusterStates.DELETED, ClusterStates.DELETING])
                print(f"🧹␡Successfully deleted {cluster_name}")
            else:
                print((f"🧹👀👍Found {cluster_name}, but its was in deleting state, so passing."))
        else:
            print(f"🧹👍No need to clean up {cluster_name}")

    def tearDown(self):
        print(f"✅✅✅✅✅✅✅✅✅✅ Tests Completed, entering tear down stage. ✅✅✅✅✅✅✅✅✅✅")
        print(f"🧹Cleaning Up, Ensuring {ephemeral_test_clusters} are not present, or is deleted/deleting.")

        for each_test_cluster in ephemeral_test_clusters:
            self.clean_up_cluster(each_test_cluster)
