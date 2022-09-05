"""
Nose2 Unit Tests for the clusters module.


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.projects import Project, ProjectSettings
from atlasapi.teams import TeamRoles
from atlasapi.atlas_users import AtlasUser
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ProjectTests(BaseTests):

    def test_00_get_projects_all_for_org_key(self):
        count = 0
        for each in self.a_owner.Projects.projects:
            # pprint(each.__dict__)
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            count += 1
        self.assertEqual(count, 4, "There should be exactly 4 projects returned when for this test Organization")
        print(f"✅ Found the expected 4 projects.")

    test_00_get_projects_all_for_org_key.basic = True

    def test_01_get_projects_all_for_proj_key(self):
        count = 0
        for each in self.a.Projects.projects:
            # pprint(each.__dict__)
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            count += 1
        self.assertEqual(count, 1, "There should be exactly 1 projects returned when for this test Project")
        print(f"✅ Found the expected 1 project.")
    test_01_get_projects_all_for_proj_key.basic = True

    def test_02_get_project_by_id(self):
        for each in self.a.Projects.projects:
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            pprint(f"👍The group_id to use is {each.id}")
            group_id = each.id
            self.assertIsInstance(each.org_id, str, "OrgID should be an str")

        out = self.a.Projects.project_by_id(group_id)
        self.assertIsInstance(out, Project, "An Atlas <Project> should be returned")
        print(f"✅ Found the expected 1 Project by id.")
    test_02_get_project_by_id.basic = True

    def test_03_get_project_by_name(self):
        for each in self.a.Projects.projects:
            self.assertIsInstance(each, Project, "An Atlas <Project should be returned>")
            pprint(f"👍The group_name to use is {each.name}")
            group_name = each.name
            self.assertIsInstance(each.name, str, "OrgID should be an str")

        out = self.a.Projects.project_by_name(group_name)
        # pprint(out.__dict__)
        self.assertIsInstance(out, Project, "An Atlas <Project> should be returned")
        print(f"✅ Found the expected 1 project by name.")
    test_03_get_project_by_name.basic = True

    def test_04_get_project_by_both_fail(self):

        with self.assertRaises(ValueError) as ex:
            pprint(f"👍Supplying both yielded exception")
            out = self.a.Projects._get_project(group_name="bad bad", group_id='anid')

    test_04_get_project_by_both_fail.basic = True

    def test_05_get_project_teams_basic(self):
        out = self.a.Projects.get_project_teams()
        for each in out:
            self.assertIsInstance(each, TeamRoles)
            self.assertIsInstance(each.roles,list,"❌Roles should be a list of strings")
            for each_role in each.roles:
                self.assertIsInstance(each_role,str, "❌Each listed role should be a string.")
        pprint(f"👍Successfully validated project getting project teams")

    test_05_get_project_teams_basic.basic = True

    def test_06_get_project_teams_pass_id(self):
        out = self.a_owner.Projects.get_project_teams(group_id=self.a.group)
        for each in out:
            self.assertIsInstance(each, TeamRoles)
            self.assertIsInstance(each.roles,list,"❌Roles should be a list of strings")
            for each_role in each.roles:
                self.assertIsInstance(each_role,str, "❌Each listed role should be a string.")
            #pprint(each.__dict__)

    test_06_get_project_teams_pass_id.basic = True

    def test_07_get_project_users_fail_noGroup(self):
        with self.assertRaises(ValueError):
            pprint(f"👍Supplying no group yielded exception")
            out = self.a_owner.Projects.get_project_users()
            for each in out:
                self.assertIsInstance(each, AtlasUser)
                #pprint(each.__dict__)

    test_07_get_project_users_fail_noGroup.basic = True

    def test_08_get_project_users(self):
        out = self.a.Projects.get_project_users()
        for each in out:
            self.assertIsInstance(each, AtlasUser)
            #pprint(each.__dict__)

    test_08_get_project_users.basic = True


    def test_09_get_project_user_count(self):
        out = self.a.Projects.user_count()
        self.assertIsInstance(out, int, "❌The count should be a in integer!")
        self.assertGreaterEqual(out, 1, "❌Should have more than one user!")
        pprint(f"👍 The count is {out}")

    test_09_get_project_user_count.basic = True

    def test_10_get_project_settings(self):
        out = self.a.Projects.settings
        #pprint(f"👍 The settings are {out.__dict__}")
        self.assertIsInstance(out, ProjectSettings, "❌The response must be a ProjectSettings obj")

    test_10_get_project_settings.basic = True
