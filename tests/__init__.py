import unittest
from os import getenv, environ
from atlasapi.atlas import Atlas
from datetime import datetime
import coolname

TEST_CLUSTER_NAME = getenv('TEST_CLUSTER_NAME', 'pyAtlasTestCluster')
TEST_CLUSTER2_NAME = getenv('TEST_CLUSTER2_NAME', 'pyAtlas-')

test_run_id = coolname.generate_slug(2)

TEST_CLUSTER_NAME_UNIQUE = TEST_CLUSTER_NAME + test_run_id
TEST_CLUSTER2_NAME_UNIQUE = TEST_CLUSTER2_NAME + test_run_id
TEST_CLUSTER3_NAME_UNIQUE = TEST_CLUSTER2_NAME + coolname.generate_slug(2)


class BaseTests(unittest.TestCase):
    def setUp(self):
        self.USER = getenv('ATLAS_USER', None)
        self.API_KEY = getenv('ATLAS_KEY', None)
        self.GROUP_ID = getenv('ATLAS_GROUP', None)

        #print("env var is".format(getenv('ATLAS_USER', None)))

        self.TEST_CLUSTER_NAME = TEST_CLUSTER_NAME
        self.TEST_CLUSTER2_NAME = TEST_CLUSTER2_NAME

        self.TEST_CLUSTER_NAME_UNIQUE = TEST_CLUSTER2_NAME_UNIQUE
        self.TEST_CLUSTER2_NAME_UNIQUE = TEST_CLUSTER2_NAME_UNIQUE
        self.TEST_CLUSTER3_NAME_UNIQUE = TEST_CLUSTER3_NAME_UNIQUE

        if not self.USER or not self.API_KEY or not self.GROUP_ID:
            raise EnvironmentError('In order to run this smoke test you need ATLAS_USER, AND ATLAS_KEY env variables'
                                   'your env variables are {}'.format(environ.__str__()))
        self.a = Atlas(self.USER, self.API_KEY, self.GROUP_ID)

    # executed after each test

    def tearDown(self):
        pass