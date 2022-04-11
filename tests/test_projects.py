"""
Nose2 Unit Tests for the clusters module.


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.projects import Project
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ProjectTests(BaseTests):

    def test_00_get_projects_all_for_org_key(self):
        count = 0
        for each in self.a_owner.Projects.get_projects():
            # pprint(each.__dict__)
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            count += 1
        self.assertEqual(count, 3, "There should be exactly 3 projects returned when for this test Organization")

    test_00_get_projects_all_for_org_key.basic = True

    def test_01_get_projects_all_for_proj_key(self):
        count = 0
        for each in self.a.Projects.get_projects():
            # pprint(each.__dict__)
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            count += 1
        self.assertEqual(count, 1, "There should be exactly 1 projects returned when for this test Project")

    test_01_get_projects_all_for_proj_key.basic = True
