"""
Nose2 Unit Tests for the clusters module.


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.organizations import Organization
from atlasapi.teams import TeamRoles
from atlasapi.atlas_users import AtlasUser
from atlasapi.projects import Project
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class ProjectTests(BaseTests):

    def test_00_get_organizations(self):
        for each in self.a.Organizations.organizations:
            self.assertIsInstance(each, Organization, "An Atlas <Organization> should be returned")

    test_00_get_organizations.basic = True

    def test_01_get_organization_by_name(self):
        for each in self.a.Organizations.organizations:
            org_name = each.name

        result = self.a.Organizations.organization_by_name(org_name=org_name)
        #pprint(result.__dict__)
        self.assertIsInstance(result, Organization, "An Atlas <Organization> should be returned")
        self.assertEqual(org_name, result.name, "Returned result was not the same.")

    test_01_get_organization_by_name.basic = True

    def test_02_get_organization_by_id(self):
        for each in self.a.Organizations.organizations:
            org_id = each.id

        result = self.a.Organizations.organization_by_id(org_id)
        #pprint(result.__dict__)
        self.assertIsInstance(result, Organization, "An Atlas <Organization> should be returned")
        self.assertEqual(org_id, result.id, "Returned result was not the same.")

    test_02_get_organization_by_id.basic = True

    def test_03_get_organization_count(self):
        result = self.a.Organizations.count
        self.assertIsInstance(result, int, "The count should be an int")

    test_03_get_organization_count.basic = True

    def test_04_get_all_projects_for_org(self):
        org_id = '5ac52173d383ad0caf52e11c'
        project_count = 0
        for each_project in self.a_owner.Organizations.get_all_projects_for_org(org_id=org_id):
            print(f"Found Project :{each_project.name}, {type(each_project)}")
            self.assertIsInstance(each_project, Project, f"The return type was not <Project>, it was {type(each_project)}")
            project_count +=1

        self.assertGreater(project_count,0, "Did not find any projects, this is a bug, or the test org is not set up "
                                            "correctly.")

    test_04_get_all_projects_for_org.basic = True



